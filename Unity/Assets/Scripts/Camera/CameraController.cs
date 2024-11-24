using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    // Start is called before the first frame update
    public Transform mainCamera;
    public float verticalOffset = 5f;
    public Transform screenshotCamera;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        mainCamera.LookAt(transform.position);
        screenshotCamera.SetPositionAndRotation(mainCamera.position, mainCamera.rotation);
    }
    public void SetPosition(float x, float z,float gridHeight)
    {
        transform.position = new Vector3(x,0,z);
        setCameraOffset(verticalOffset,gridHeight);
        if(ExperimentManager.Instance != null)
        { 
            LandmarkData laodedData = ExperimentManager.Instance.loadedLandmarkData;
            Vector3 cameraLocalPosition = new Vector3(laodedData.camera_offset[0],laodedData.camera_offset[1], laodedData.camera_offset[2]);
            if(cameraLocalPosition != Vector3.zero)
                setCameraOffset(cameraLocalPosition);
        }
    }
    private void setCameraOffset(float yOffset , float zOffset)
    {
        mainCamera.localPosition = new Vector3(0,yOffset,-1 * zOffset);
        mainCamera.LookAt(transform.position);
    }
    private void setCameraOffset(Vector3 position)
    {
        mainCamera.localPosition = position;
        mainCamera.LookAt(transform.position);
    }
}
