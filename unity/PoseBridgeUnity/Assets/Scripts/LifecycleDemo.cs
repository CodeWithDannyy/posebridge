using UnityEngine;

// Logs each Unity lifecycle method so we can watch the engine call our code,
// and spins the object to show frame-rate-independent movement.
public class LifecycleDemo : MonoBehaviour
{
    [SerializeField] float degreesPerSecond = 90f;

    int frameCount;

    void Awake()
    {
        Debug.Log("Awake: object created");
    }

    void Start()
    {
        Debug.Log("Start: just before the first frame");
    }

    void Update()
    {
        frameCount++;

        // Time.deltaTime = seconds since the previous frame.
        transform.Rotate(0f, degreesPerSecond * Time.deltaTime, 0f);

        if (frameCount % 60 == 0)
        {
            Debug.Log($"Update: frame {frameCount}, {1f / Time.deltaTime:F0} fps, frame took {Time.deltaTime * 1000f:F1} ms");
        }
    }

    void OnDestroy()
    {
        Debug.Log("OnDestroy: object removed");
    }
}
