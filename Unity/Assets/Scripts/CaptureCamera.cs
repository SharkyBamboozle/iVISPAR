using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class CaptureCamera : MonoBehaviour
{
    public float captureRate = 2f;
    public bool shouldAutoCapture = false;
    private Camera myCamera;
    private IEnumerator SaveScreenShot()
    {
        while(true)
        {
            ScreenCapture.CaptureScreenshot("SomeLevel.png");
            yield return new WaitForSeconds(captureRate);
        }
    }
    void Start()
    {
        Debug.Log(Application.persistentDataPath);
        myCamera = GetComponent<Camera>();
        if(shouldAutoCapture)
        {
            StartCoroutine(SaveScreenShot());
        }    
    }
    private void OnDestroy() {
        StopAllCoroutines();
    }
    // Update is called once per frame
    void Update()
    {
        if(Input.GetKeyDown(KeyCode.Space))
            CaptureFrame("capturing");    
    }
    
    public void CaptureFrame(string path, string extension = ".png")
    {
        Debug.Log("capturing");
        ScreenCapture.CaptureScreenshot(path + extension);
    }
}
