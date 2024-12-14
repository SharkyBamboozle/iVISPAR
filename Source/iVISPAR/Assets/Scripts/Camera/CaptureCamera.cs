using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

public class CaptureCamera : MonoBehaviour
{
    private Camera screenshotCamera;
    public RenderTexture userPhoto; // Assign the RenderTexture in the Inspector
    public bool imageToggle = true;
    [Range(0f,1f)]
    public float percentage = 0.3f;
    private string boardSatus = "";
    public int fontSize = 20;
    public Vector2 lableSize = new Vector2(300,200);
    public Vector2 lablePosition = new Vector2(10,10);

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
        if(ExperimentManager.Instance.humanExperiment)
            screenshotCamera.backgroundColor = new Color(screenshotCamera.backgroundColor.r , screenshotCamera.backgroundColor.g, screenshotCamera.backgroundColor.b,0f);
        else
            screenshotCamera.backgroundColor = new Color(screenshotCamera.backgroundColor.r , screenshotCamera.backgroundColor.g, screenshotCamera.backgroundColor.b,alpha);
    }
    void Update()
    {
        if(ExperimentManager.Instance.humanExperiment)
        {
            if(Input.GetKeyDown(KeyCode.Space))
            {
                imageToggle = !imageToggle;
            }
        }
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
        if (userPhoto == null)
        {
            userPhoto = new RenderTexture(renderTexture.width, renderTexture.height, renderTexture.depth);
            Graphics.Blit(renderTexture, userPhoto); // Copy the contents of renderTexture to userPhoto
        }
        if(!ExperimentManager.Instance.loadedLandmarkData.use_rendering && boardSatus == "")
        {
            GameObject[] boardObjects = GameObject.FindGameObjectsWithTag("Commandable");
            foreach (GameObject boardObject in boardObjects)
            {
                boardSatus += (boardObject.GetComponent<TargetBehaviour>().getObjectChessStatus() + "\n");
            }
        }
        byte[] screenshot = texture.GetRawTextureData();
        Debug.LogWarning("Texture size is " + texture.width.ToString() + " * " + texture.height.ToString() + " with total size of " + screenshot.Length + " bytes");
        List<string> screenshotInfo = new List<string>();
        screenshotInfo.Add(texture.width.ToString());
        screenshotInfo.Add(texture.height.ToString());
        Debug.Log("sending Screenshot command");
        DataPacket data = NetworkManger.Instance.PackData("ActionAck",new List<string>(), screenshot);
        EventHandler.Instance.InvokeCommand("ActionAck",data);
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
        
        DataPacket data = NetworkManger.Instance.PackData("ActionAck",new List<string>(), screenshot);
        EventHandler.Instance.InvokeCommand("ActionAck",data);
        UnityEngine.Object.Destroy(texture);
        yield return null;
    }

    

    void OnGUI()
    {
        if(ExperimentManager.Instance.loadedLandmarkData.use_rendering && ExperimentManager.Instance.humanExperiment)
        {
            if (userPhoto != null)
            {
                if(imageToggle)
                {
                    float DIMENTION = Screen.width * percentage;
                    GUI.DrawTexture(new Rect(20, 20, DIMENTION, DIMENTION), userPhoto, ScaleMode.ScaleToFit, false);
                }
            }
        }
        else if (!ExperimentManager.Instance.loadedLandmarkData.use_rendering && ExperimentManager.Instance.humanExperiment)
        {
            if (boardSatus != "")
            {
                if(imageToggle)
                {
                    GUIStyle style = new GUIStyle(GUI.skin.label);
                    style.alignment = TextAnchor.MiddleCenter;
                    style.fontSize = fontSize;
                    style.clipping = TextClipping.Overflow;
                    // Calculate a rect that is centered on the screen
                    Rect rect = new Rect(
                        lablePosition.x,lablePosition.y, 
                        lableSize.x,lableSize.y
                    );
                    
                    GUI.Label(rect, boardSatus, style);
                }      
            }
        }
    }
    
}
