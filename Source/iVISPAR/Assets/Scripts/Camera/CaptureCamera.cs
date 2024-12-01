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
        float alpha = 1f;
        if(EventHandler.Instance != null)
        {
            EventHandler.Instance.RegisterEvent("capture_send_screenshot",GenerateScreenshot);
            EventHandler.Instance.RegisterEvent("capture_screenshot_for_ack",GenerateAckScreenshot);
            alpha = ExperimentManager.Instance.loadedLandmarkData.screenshot_alpha;
             
        }
        screenshotCamera.backgroundColor = new Color(screenshotCamera.backgroundColor.r , screenshotCamera.backgroundColor.g, screenshotCamera.backgroundColor.b,alpha);
    }
    private void OnDestroy() {
        StopAllCoroutines();
        if(EventHandler.Instance != null)
        {
            EventHandler.Instance.UnregisterEvent("capture_send_screenshot",GenerateScreenshot);
            EventHandler.Instance.UnregisterEvent("capture_screenshot_for_ack",GenerateAckScreenshot);
        }
    }
    // Update is called once per frame
    public void GenerateScreenshot()
    {
        StartCoroutine("RecordFrameFromTexture");
    }
    public void GenerateAckScreenshot()
    {
        StartCoroutine("RecordFrameFromTextureAck");
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
        List<string> screenshotInfo = new List<string>();
        screenshotInfo.Add(texture.width.ToString());
        screenshotInfo.Add(texture.height.ToString());
        DataPacket data = NetworkManger.Instance.PackData("Screenshot",screenshotInfo, screenshot);
        
        if(!InteractionUI.Instance.IsHumanExperiment())
            NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(data));
        else
        {
            InteractionUI.Instance.saveActionAck(JsonUtility.ToJson(data));
        }
        UnityEngine.Object.Destroy(texture);
        yield return null;
    }
    IEnumerator RecordFrameFromTextureAck()
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
        DataPacket data = NetworkManger.Instance.PackData("ActionAck",new List<string>(), screenshot);
        EventHandler.Instance.InvokeCommand("ActionAck",data);
        UnityEngine.Object.Destroy(texture);
        yield return null;
    }
    
}
