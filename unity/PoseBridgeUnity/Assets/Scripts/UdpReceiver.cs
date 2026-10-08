using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

// Mirrors the JSON packet defined in perception/packet.py.
// Field names must match the JSON keys exactly for JsonUtility to fill them.
[Serializable]
public class PosePacket
{
    public int v;
    public int frame;
    public double t_capture_ms;   // Unix time in ms; double because it is too big for a float
    public bool tracked;
    public float[] joints;        // image landmarks, flat: x0, y0, z0, vis0, x1, ... (0-1 fractions)
    public float[] world;         // world landmarks, same layout, in metres from the hip midpoint (v2)
}

// Listens for packets on a background thread and exposes the newest one to the main thread.
public class UdpReceiver : MonoBehaviour
{
    const int ExpectedSchemaVersion = 2;

    [SerializeField] int port = 5005;   // must match perception/udp.py

    // The most recent packet. Read this from Update() in other scripts.
    public PosePacket Latest { get; private set; }

    UdpClient client;
    Thread thread;

    // Shared between the background thread (writes) and the main thread (reads).
    readonly object gate = new object();
    string latestJson;
    double latestReceivedMs;   // stamped the instant the packet came off the socket
    int latestVersion;
    int seenVersion;

    // Debug statistics, main thread only.
    int lastFrame = -1;
    int missed;
    int packetsThisSecond;
    float nextReportTime;
    double transportSum, transportMax;   // Python capture -> socket receive
    double pollSum, pollMax;             // socket receive -> Unity Update picks it up

    static double NowMs() => (DateTime.UtcNow - DateTime.UnixEpoch).TotalMilliseconds;

    void Start()
    {
        // Loopback only: reachable from this computer, not from the network.
        client = new UdpClient(new IPEndPoint(IPAddress.Loopback, port));
        thread = new Thread(ReceiveLoop) { IsBackground = true, Name = "PoseBridge UDP" };
        thread.Start();
        Debug.Log($"UdpReceiver listening on 127.0.0.1:{port}");
    }

    // Runs on the BACKGROUND thread. Keep it dumb: no Unity API, no parsing.
    void ReceiveLoop()
    {
        var remote = new IPEndPoint(IPAddress.Any, 0);
        try
        {
            while (true)
            {
                byte[] data = client.Receive(ref remote);   // blocks until a packet arrives
                double receivedMs = NowMs();                // stamp immediately
                string json = Encoding.UTF8.GetString(data);
                lock (gate)
                {
                    latestJson = json;   // newer packet replaces an unread older one
                    latestReceivedMs = receivedMs;
                    latestVersion++;
                }
            }
        }
        catch (SocketException) { }          // client was closed by OnDestroy: normal shutdown
        catch (ObjectDisposedException) { }  // same
    }

    // Runs on the MAIN thread, once per Unity frame.
    void Update()
    {
        string json = null;
        double receivedMs = 0;
        lock (gate)
        {
            if (latestVersion != seenVersion)
            {
                json = latestJson;
                receivedMs = latestReceivedMs;
                seenVersion = latestVersion;
            }
        }

        if (json != null)
        {
            Latest = JsonUtility.FromJson<PosePacket>(json);
            OnNewPacket(Latest, receivedMs);
        }

        if (Time.unscaledTime >= nextReportTime)
        {
            ReportStats();
            nextReportTime = Time.unscaledTime + 1f;
        }
    }

    void OnNewPacket(PosePacket packet, double receivedMs)
    {
        if (packet.v != ExpectedSchemaVersion)
        {
            Debug.LogWarning($"Packet schema v{packet.v}, expected v{ExpectedSchemaVersion}");
        }

        // A jump in the frame counter = packets lost, or overwritten before we read them.
        if (lastFrame >= 0 && packet.frame > lastFrame + 1)
        {
            missed += packet.frame - lastFrame - 1;
        }
        lastFrame = packet.frame;
        packetsThisSecond++;

        // Split the delay into two parts so we can see which one is large.
        double transport = receivedMs - packet.t_capture_ms;
        double poll = NowMs() - receivedMs;
        transportSum += transport;
        pollSum += poll;
        transportMax = Math.Max(transportMax, transport);
        pollMax = Math.Max(pollMax, poll);
    }

    void ReportStats()
    {
        if (Latest == null)
        {
            Debug.Log("UdpReceiver: waiting for packets...");
            return;
        }

        int n = Math.Max(packetsThisSecond, 1);
        Debug.Log($"UDP: {packetsThisSecond} pkt/s | tracked={Latest.tracked} | missed total {missed} | " +
                  $"capture->socket avg {transportSum / n:F1} (max {transportMax:F1}) ms | " +
                  $"socket->Update avg {pollSum / n:F1} (max {pollMax:F1}) ms | " +
                  $"Unity {1f / Time.unscaledDeltaTime:F0} fps");

        packetsThisSecond = 0;
        transportSum = transportMax = pollSum = pollMax = 0;
    }

    // Closing the socket makes the blocked Receive() throw, which ends the thread.
    // Without this the port stays taken and the next Play press fails.
    void OnDestroy()
    {
        client?.Close();
        thread?.Join(500);
    }
}
