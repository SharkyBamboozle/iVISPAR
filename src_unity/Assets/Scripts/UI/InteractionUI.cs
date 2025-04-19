
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using System.IO;
using System.Runtime.InteropServices;
using System;
#if UNITY_EDITOR
using UnityEditor;
#endif
public class InteractionUI : MonoBehaviour
{
    public static InteractionUI Instance;
    public float textFieldWidthPercentage = 0.75f; // 75% of the screen width
    public float buttonWidthPercentage = 0.2f;    // 20% of the screen width
    public float heightPercentage = 0.1f;         // 10% of the screen height
    public float messageFontRatio = 0.03f;
    public int ButtonFontSize = 20;
    public bool isHumanExperiment = false;
    private string inputText = "";
    private GUIStyle textFieldStyle;
    private GUIStyle buttonStyle;
    
    public bool isLevelLoaded = false;
    private List<string> humanLogs;
    
    public CaptureCamera captureCamera;
    [DllImport("__Internal")]
    private static extern void OpenFileDialog(string ObjectName, string Target);
    public void setHumanExperiment(bool isHumanExperiment)
    {
        this.isHumanExperiment = isHumanExperiment;
    }
    public bool IsHumanExperiment()
    {
        return this.isHumanExperiment;
    }
    void Awake()
    {
        // Singleton pattern
        if (Instance != null && Instance != this) 
        { 
            Destroy(this); 
        } 
        else 
        { 
            Instance = this; 
            humanLogs = new List<string>();
            DontDestroyOnLoad(gameObject);
            
        }    
    }

    // Start is called before the first frame update
    void Start()
    {
        
    }
    public List<string> getLog()
    {
        return humanLogs;
    }
    // Update is called once per frame
    void Update()
    {
        if(isLevelLoaded && captureCamera != null)
        {
            if(Input.GetKey(KeyCode.LeftControl) || Input.GetKey(KeyCode.RightControl))
            {
                //imageToggle = !imageToggle;
                captureCamera.imageToggle = true;
            }
            else
                captureCamera.imageToggle = false;
        }
    }
    public void refocusGUI(string controlName)
    {
        GUI.FocusControl(controlName);
    }
     void OnGUI() {
        if(isHumanExperiment && isLevelLoaded)
        {
            textFieldStyle = new GUIStyle(GUI.skin.textField);
            buttonStyle = new GUIStyle(GUI.skin.button);
            
            // Calculate dimensions
            float textFieldWidth = Screen.width * textFieldWidthPercentage;
            float buttonWidth = Screen.width * buttonWidthPercentage;
            float elementHeight = Screen.height * heightPercentage;
            textFieldStyle.wordWrap = true;         // Disable multi-line behavior
            textFieldStyle.clipping = TextClipping.Clip; // Allow horizontal overflow
            textFieldStyle.alignment = TextAnchor.UpperLeft; // Align text to the left
            textFieldStyle.fontSize = Mathf.RoundToInt(Screen.height * messageFontRatio); // Font size for text field
            buttonStyle.fontSize = ButtonFontSize;
            // Set up a GUILayout area at the bottom of the screen
            GUILayout.BeginArea(new Rect(0, Screen.height - elementHeight, Screen.width, elementHeight));

            // Create a horizontal layout for the text box and button
            GUILayout.BeginHorizontal();
            // Create a text box and store the user input in the 'inputText' variable
            GUI.SetNextControlName("InputField");
            inputText = GUILayout.TextField(inputText,textFieldStyle, GUILayout.Width(textFieldWidth), GUILayout.Height(elementHeight));
            if (Event.current.keyCode == KeyCode.Return)
            {
                if (GUI.GetNameOfFocusedControl() == "InputField")
                {
                   if(inputText != "")
                    {
                        List<string> commands = inputText.Split(",").ToList();
                        UserInteraction(commands);
                        inputText = "";
                        //Event.current.Use();
                    }
                }
            }
            else if(Event.current.keyCode == KeyCode.LeftControl)
            {
                if(Event.current.type == EventType.KeyUp)
                    captureCamera.HandleEvent(Event.current,false);
                else
                    captureCamera.HandleEvent(Event.current,true);
            }
            // Create a button next to the text box
            if (GUILayout.Button("Submit",buttonStyle, GUILayout.Width(buttonWidth), GUILayout.Height(elementHeight)))
            {
                if(inputText != "")
                {
                    List<string> commands = inputText.Split(",").ToList();
                    UserInteraction(commands);
                    inputText = "";
                }
            }

            // End the horizontal layout
            GUILayout.EndHorizontal();

            // End the GUILayout area
            GUILayout.EndArea();
        }
        else if(isHumanExperiment && !isLevelLoaded)
        {
               textFieldStyle = new GUIStyle(GUI.skin.textField);
            buttonStyle = new GUIStyle(GUI.skin.button);
            
            // Calculate dimensions
            float textFieldWidth = Screen.width * textFieldWidthPercentage;
            float buttonWidth = Screen.width * buttonWidthPercentage;
            float elementHeight = Screen.height * heightPercentage;
            textFieldStyle.wordWrap = true;         // Disable multi-line behavior
            textFieldStyle.clipping = TextClipping.Clip; // Allow horizontal overflow
            textFieldStyle.alignment = TextAnchor.UpperLeft; // Align text to the left
            textFieldStyle.fontSize = Mathf.RoundToInt(Screen.height * messageFontRatio); // Font size for text field
            
            buttonStyle.fontSize = ButtonFontSize;
            // Set up a GUILayout area at the bottom of the screen
            GUILayout.BeginArea(new Rect(0, Screen.height - elementHeight, Screen.width, elementHeight));

            // Create a horizontal layout for the text box and button
            GUILayout.BeginHorizontal();
            
            // Create a text box and store the user input in the 'inputText' variable
            GUI.enabled = false;
            inputText = GUILayout.TextField(inputText,textFieldStyle, GUILayout.Width(textFieldWidth), GUILayout.Height(elementHeight));
            GUI.enabled = true;
            // Create a button next to the text box
            if (GUILayout.Button("Start!",buttonStyle, GUILayout.Width(buttonWidth), GUILayout.Height(elementHeight)))
            {
                
                OpenFileSelector();
            }

            // End the horizontal layout
            GUILayout.EndHorizontal();

            // End the GUILayout area
            GUILayout.EndArea();
        }
    }
    
    public void saveActionAck(string data)
    {
        humanLogs.Add(data);
    }
    public void UserInteraction(List<string> command)
    {
        DataPacket fakeData = new DataPacket();
        fakeData.command = "GameInteraction";
        fakeData.messages = command ;
        EventHandler.Instance.InvokeCommand("GameInteraction",fakeData);
    }

    public void OpenFileSelector()
    {
#if UNITY_EDITOR
        OpenFileInEditor();
#elif UNITY_WEBGL && !UNITY_EDITOR
        OpenFileDialog(this.gameObject.name, "OnFileSelected");
#else
        Debug.LogWarning("File selection only works in Unity Editor or WebGL builds.");
#endif
    }
#if UNITY_EDITOR
    private void OpenFileInEditor()
    {
        string path = EditorUtility.OpenFilePanel("Select experiment txt File", "", "txt");
        if (!string.IsNullOrEmpty(path))
        {
            Debug.Log("File selected: " + path);
            
            // Read the file content
            string fileContent = File.ReadAllText(path);
            // Call OnFileSelected with the file content (mimicking WebGL behavior)
            OnFileSelected(Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes(fileContent)));
        }
    }
#endif
    public void OnFileSelected(string base64Data)
    {
        Debug.Log("File selected. Base64 data length: " + base64Data.Length);
#if UNITY_EDITOR
        byte[] fileData = Convert.FromBase64String(base64Data);
        string fileText = System.Text.Encoding.UTF8.GetString(fileData);
#elif UNITY_WEBGL && ! UNITY_EDITOR
        Debug.Log(base64Data);
        string fileText = base64Data;
#endif
       
        ExperimentManager.Instance.SetConfigList(fileText);
        
    }
    
}
