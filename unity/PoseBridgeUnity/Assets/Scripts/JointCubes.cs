using UnityEngine;

// Spawns one cube per pose joint and moves the cubes to follow UdpReceiver.Latest.
// First version: deliberately naive coordinates. Step 6 fixes them.
public class JointCubes : MonoBehaviour
{
    const int JointCount = 33;
    const int Stride = 4;   // numbers per joint in the packet: x, y, z, visibility

    [SerializeField] UdpReceiver receiver;
    [SerializeField] float scale = 10f;          // image fraction (0-1) -> Unity units
    [SerializeField] float cubeSize = 0.25f;
    [SerializeField] float minVisibility = 0.5f; // hide joints the model is unsure about

    Transform[] cubes;

    void Start()
    {
        cubes = new Transform[JointCount];
        for (int i = 0; i < JointCount; i++)
        {
            GameObject cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
            cube.name = $"Joint {i}";
            cube.transform.SetParent(transform, false);   // keep the scene tidy under this object
            cube.transform.localScale = Vector3.one * cubeSize;
            Destroy(cube.GetComponent<Collider>());       // we only need to see them
            cube.GetComponent<Renderer>().material.color = ColorFor(i);
            cubes[i] = cube.transform;
        }
    }

    void Update()
    {
        PosePacket packet = receiver.Latest;
        bool hasPose = packet != null && packet.tracked &&
                       packet.joints != null && packet.joints.Length == JointCount * Stride;

        for (int i = 0; i < JointCount; i++)
        {
            if (!hasPose || packet.joints[i * Stride + 3] < minVisibility)
            {
                cubes[i].gameObject.SetActive(false);
                continue;
            }

            float x = packet.joints[i * Stride];
            float y = packet.joints[i * Stride + 1];

            cubes[i].gameObject.SetActive(true);
            cubes[i].localPosition = new Vector3(x, y, 0f) * scale;   // z ignored for now
        }
    }

    // Same colour code as the Python skeleton: left orange, right light blue, centre green.
    static Color ColorFor(int i)
    {
        if (i == 0) return Color.green;                                   // nose
        bool left = i <= 10 ? (i <= 3 || i == 7 || i == 9) : i % 2 == 1; // MediaPipe numbering
        return left ? new Color(1f, 0.65f, 0f) : new Color(0f, 0.78f, 1f);
    }
}
