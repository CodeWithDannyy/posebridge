using UnityEngine;

// Step 5 playground: rotate one bone by hand, or aim it at a target object.
// Attach to the character (the object with the Humanoid Animator).
// A learning tool only; the real retargeting comes in Step 6.
[RequireComponent(typeof(Animator))]
public class RotationLab : MonoBehaviour
{
    public enum Mode { RotateLocal, RotateWorld, AimAtTarget }

    [SerializeField] Mode mode = Mode.RotateLocal;
    [SerializeField] HumanBodyBones bone = HumanBodyBones.LeftUpperArm;
    [SerializeField] HumanBodyBones childBone = HumanBodyBones.LeftLowerArm; // tells us which way the bone points
    [SerializeField] Vector3 axis = Vector3.forward;                         // axis for the Rotate modes
    [SerializeField, Range(-180f, 180f)] float angle = 0f;
    [SerializeField] Transform target;                                       // AimAtTarget: a sphere you drag around

    Transform boneTransform;
    Transform childTransform;
    Quaternion restLocal;      // the bone's rotation relative to its parent, in the T-pose
    Quaternion restWorld;      // the bone's rotation relative to the scene, in the T-pose
    Vector3 restDirection;     // which way the bone points in the T-pose (world space, length 1)

    void Start()
    {
        Animator animator = GetComponent<Animator>();
        boneTransform = animator.GetBoneTransform(bone);
        childTransform = animator.GetBoneTransform(childBone);

        // Remember the rest pose once, before we change anything.
        restLocal = boneTransform.localRotation;
        restWorld = boneTransform.rotation;
        restDirection = (childTransform.position - boneTransform.position).normalized;

        Debug.Log($"{bone} at rest: local euler {restLocal.eulerAngles}, world euler {restWorld.eulerAngles}, " +
                  $"points along {restDirection}");
    }

    void LateUpdate()
    {
        Quaternion turn = Quaternion.AngleAxis(angle, axis);

        switch (mode)
        {
            case Mode.RotateLocal:
                // Rest, then turn around the BONE's own axis.
                boneTransform.localRotation = restLocal * turn;
                break;

            case Mode.RotateWorld:
                // Rest, then turn around the WORLD's axis.
                boneTransform.rotation = turn * restWorld;
                break;

            case Mode.AimAtTarget:
                if (target == null) return;
                // Which way should the bone point now?
                Vector3 wanted = (target.position - boneTransform.position).normalized;
                // The smallest turn from "how it points at rest" to "how it should point",
                // applied on top of the rest rotation. This line IS retargeting, for one bone.
                boneTransform.rotation = Quaternion.FromToRotation(restDirection, wanted) * restWorld;
                break;
        }
    }

    // Yellow line along the bone, red line to the target (Scene view only).
    void OnDrawGizmos()
    {
        if (boneTransform == null) return;
        Gizmos.color = Color.yellow;
        Gizmos.DrawLine(boneTransform.position, childTransform.position);
        if (mode == Mode.AimAtTarget && target != null)
        {
            Gizmos.color = Color.red;
            Gizmos.DrawLine(boneTransform.position, target.position);
        }
    }
}
