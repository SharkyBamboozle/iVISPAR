using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

public class CameraController : MonoBehaviour
{
    // Start is called before the first frame update
    public Transform mainCamera;
    public float verticalOffset = 5f;
    public Transform screenshotCamera;
    public int fontSize = 30;
    public Vector2 lableSize = new Vector2(800,600);
    public Vector2 lableOffset = new Vector2(0,150);
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
        Vector3 overrideAutoPosition = Vector3.zero;
        if(ExperimentManager.Instance != null)
        {
            LandmarkData laodedData = ExperimentManager.Instance.loadedLandmarkData;
            overrideAutoPosition = new Vector3(laodedData.camera_auto_override[0],laodedData.camera_auto_override[1], laodedData.camera_auto_override[2]);
        }

        transform.position = new Vector3(x,0,z);
        if(overrideAutoPosition != Vector3.zero)
            transform.position = overrideAutoPosition;
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
    void OnGUI() {
        if(ExperimentManager.Instance.humanExperiment && !ExperimentManager.Instance.loadedLandmarkData.use_rendering)
        {
            GUIStyle style = new GUIStyle(GUI.skin.label);
            style.alignment = TextAnchor.MiddleCenter;
            style.fontSize = fontSize;
            style.clipping = TextClipping.Overflow;

            // Calculate a rect that is centered on the screen
            Rect rect = new Rect(
                ((Screen.width - lableSize.x) / 2) - lableOffset.x, 
                ((Screen.height - lableSize.y) / 2) - lableOffset.y, 
                lableSize.x,lableSize.y
            );
            string boardSatus = "";
            GameObject[] boardObjects = GameObject.FindGameObjectsWithTag("Commandable");
            foreach (GameObject boardObject in boardObjects)
            {
                boardSatus += (boardObject.GetComponent<TargetBehaviour>().getObjectChessStatus() + "\n");
            }
            GUI.Label(rect, boardSatus, style);
        }   
    }
}
