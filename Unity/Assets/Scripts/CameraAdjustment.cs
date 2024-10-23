using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CameraAdjustment : MonoBehaviour
{
    // Start is called before the first frame update
    public List<Transform> screenshotCameras;
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void SetPostition(float x, float z)
    {
        transform.position = new Vector3(x,transform.position.y,z); 
        if(screenshotCameras.Count != 0)
            foreach(Transform cam in screenshotCameras)
                cam.position = new Vector3(x,transform.position.y,z); 
    }
}
