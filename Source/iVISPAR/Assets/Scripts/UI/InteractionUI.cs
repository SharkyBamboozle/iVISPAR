
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
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

    // Update is called once per frame
    void Update()
    {
        if(Input.GetKeyDown(KeyCode.Return) && isLevelLoaded)
        {
            if(inputText != "")
            {
                List<string> commands = inputText.Split(",").ToList();
                UserInteraction(commands);
                inputText = "";
            }
        }
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
            inputText = GUILayout.TextField(inputText,textFieldStyle, GUILayout.Width(textFieldWidth), GUILayout.Height(elementHeight));

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
}
