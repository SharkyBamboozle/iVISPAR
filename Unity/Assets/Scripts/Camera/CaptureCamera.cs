using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class CaptureCamera : MonoBehaviour
{
    private Camera screenshotCamera;
    
    void OnEnable(){
        screenshotCamera = this.GetComponent<Camera>();
    }
    void Start()
    {
        EventHandler.Instance.RegisterEvent("capture_send_screenshot",GenerateScreenshot);
    }
    private void OnDestroy() {
        StopAllCoroutines();
    }
    // Update is called once per frame
    void Update()
    {
          
    }
    public void GenerateScreenshot()
    {
        StartCoroutine("RecordFrameFromTexture");
    }
    IEnumerator RecordFrameFromTexture()
    {
        yield return new WaitForEndOfFrame();
        Rect rect = new Rect(0, 0, screenshotCamera.pixelWidth, screenshotCamera.pixelHeight);
        RenderTexture renderTexture = new RenderTexture(screenshotCamera.pixelWidth, screenshotCamera.pixelHeight, 24);
        Texture2D texture = new Texture2D(screenshotCamera.pixelWidth, screenshotCamera.pixelHeight, TextureFormat.RGBA32, false);
        screenshotCamera.targetTexture = renderTexture;
        screenshotCamera.Render();
        RenderTexture.active = renderTexture;
        texture.ReadPixels(rect, 0, 0);
        texture.Apply();
        screenshotCamera.Render();
        byte[] screenshot = texture.GetRawTextureData();
        Debug.LogWarning("Texture size is " + texture.width.ToString() + " * " + texture.height.ToString() + " with total size of " + screenshot.Length + " bytes");
        DataPacket data = NetworkManger.Instance.PackData("Screenshot","Starting screenshot", screenshot);
        NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(data));
        UnityEngine.Object.Destroy(texture);
        yield return null;
    }
    
}
