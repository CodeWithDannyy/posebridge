using UnityEngine;

// Spawns one cube per pose joint and moves the cubes to follow UdpReceiver.Latest.
// Converts the packet's image coordinates into Unity world coordinates.
public class JointCubes : MonoBehaviour
{
    const int JointCount = 33;
    const int Stride = 4;   // numbers per joint in the packet: x, y, z, visibility
    const int LeftHip = 23;
    const int RightHip = 24;

    [SerializeField] UdpReceiver receiver;
    [SerializeField] bool useWorld = true;        // true: 3D world landmarks (metres); false: image
    [SerializeField] float worldScale = 2.5f;     // Unity units per metre (world mode)
    [SerializeField] float scale = 6f;            // Unity units per image height (image mode)
    [SerializeField] float imageAspect = 4f / 3f; // webcam width / height (640x480)
    [SerializeField] bool mirror = true;          // act like a mirror, not like a photo
    [SerializeField] bool anchorToHips = true;    // true: pose only; false: also walk around
    [SerializeField] float depthFactor = 0f;      // 0 = flat; try 1 to see how noisy z is
    [SerializeField] float cubeSize = 0.2f;
    [SerializeField] float minVisibility = 0.5f;  // hide joints the model is unsure about

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
                       packet.joints != null && packet.joints.Length == JointCount * Stride &&
                       Visible(packet.joints, LeftHip) && Visible(packet.joints, RightHip);

        if (!hasPose)
        {
            SetAllActive(false);
            return;
        }

        float[] j = packet.joints;
        bool world = useWorld && packet.world != null && packet.world.Length == JointCount * Stride;
        if (world)
        {
            for (int i = 0; i < JointCount; i++)
            {
                bool show = Visible(j, i);
                cubes[i].gameObject.SetActive(show);
                if (show)
                {
                    cubes[i].localPosition = WorldToUnity(packet.world, i);
                }
            }
            return;
        }

        // Origin of the skeleton in image space: the midpoint of the hips, or the image centre.
        float originX = 0.5f;
        float originY = 0.5f;
        if (anchorToHips)
        {
            originX = (j[LeftHip * Stride] + j[RightHip * Stride]) / 2f;
            originY = (j[LeftHip * Stride + 1] + j[RightHip * Stride + 1]) / 2f;
        }

        for (int i = 0; i < JointCount; i++)
        {
            bool show = Visible(j, i);
            cubes[i].gameObject.SetActive(show);
            if (show)
            {
                cubes[i].localPosition = ToUnity(j, i, originX, originY);
            }
        }
    }

    bool Visible(float[] j, int i) => j[i * Stride + 3] >= minVisibility;

    // Image space: x right, y DOWN, both 0-1 fractions of the image size.
    // Unity space: x right, y UP, in world units.
    Vector3 ToUnity(float[] j, int i, float originX, float originY)
    {
        float dx = j[i * Stride] - originX;
        float dy = j[i * Stride + 1] - originY;

        // Multiplying x by the aspect ratio makes one unit mean the same distance in x and y;
        // without it the body would be stretched, because the image is wider than tall.
        float x = (mirror ? -dx : dx) * imageAspect * scale;
        float y = -dy * scale;                           // flip: image y points down
        float z = j[i * Stride + 2] * depthFactor * scale;
        return new Vector3(x, y, z);
    }

    // MediaPipe world space: metres from the hip midpoint, x right, y DOWN, z AWAY from camera.
    // Unity space: x right, y UP, z away from the camera (it looks along +z).
    // So only y flips (plus x for mirror mode). Already hip-centred and already in metres:
    // no aspect ratio, no origin to subtract.
    Vector3 WorldToUnity(float[] w, int i)
    {
        float x = w[i * Stride];
        float y = w[i * Stride + 1];
        float z = w[i * Stride + 2];
        return new Vector3(mirror ? -x : x, -y, z) * worldScale;
    }

    void SetAllActive(bool active)
    {
        foreach (Transform cube in cubes)
        {
            cube.gameObject.SetActive(active);
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
