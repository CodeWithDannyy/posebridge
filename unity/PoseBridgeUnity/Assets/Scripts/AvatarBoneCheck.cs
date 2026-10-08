using UnityEngine;

// Checks that the character was imported as a Humanoid and finds the bones we will drive.
// Attach to the character (the object with the Animator). Prints one line per bone on Play.
[RequireComponent(typeof(Animator))]
public class AvatarBoneCheck : MonoBehaviour
{
    // Unity's standard humanoid bone names: the same on every Humanoid model,
    // whatever the model itself calls them (e.g. "mixamorig:LeftArm" -> LeftUpperArm).
    static readonly HumanBodyBones[] BonesWeDrive =
    {
        HumanBodyBones.Hips, HumanBodyBones.Spine, HumanBodyBones.Chest,
        HumanBodyBones.Neck, HumanBodyBones.Head,
        HumanBodyBones.LeftUpperArm, HumanBodyBones.LeftLowerArm, HumanBodyBones.LeftHand,
        HumanBodyBones.RightUpperArm, HumanBodyBones.RightLowerArm, HumanBodyBones.RightHand,
        HumanBodyBones.LeftUpperLeg, HumanBodyBones.LeftLowerLeg, HumanBodyBones.LeftFoot,
        HumanBodyBones.RightUpperLeg, HumanBodyBones.RightLowerLeg, HumanBodyBones.RightFoot,
    };

    void Start()
    {
        Animator animator = GetComponent<Animator>();
        if (!animator.isHuman)
        {
            Debug.LogError("Not a Humanoid: select the FBX, Rig tab > Animation Type = Humanoid, Apply.");
            return;
        }

        int missing = 0;
        foreach (HumanBodyBones bone in BonesWeDrive)
        {
            Transform t = animator.GetBoneTransform(bone);
            if (t == null)
            {
                missing++;
                Debug.LogWarning($"{bone}: MISSING");
            }
            else
            {
                Debug.Log($"{bone} -> '{t.name}'");
            }
        }
        Debug.Log($"AvatarBoneCheck: {BonesWeDrive.Length - missing}/{BonesWeDrive.Length} bones found");
    }
}
