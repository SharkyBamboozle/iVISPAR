using System;
using System.Collections.Generic;
using System.Data.Common;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Text;
using System.Text.RegularExpressions;
using UnityEngine;

public class TurnManager : MonoBehaviour
{
    // Start is called before the first frame update
    private List<string> turnCommands;
    private bool isPuzzleSolved = false;
    bool recievedDoneCommand = false;
    private int command_count = 0;
    private int action_count = 0;
    private Color originalCameraBackground;
    public Color solvedCameraBackground;
    private Dictionary<string, int> wordToNumber = new Dictionary<string, int>
    {
        {"one", 1}, {"two", 2}, {"three", 3}, {"four", 4}, {"five", 5},
        {"six", 6}, {"seven", 7}, {"eight", 8}, {"nine", 9}, {"ten", 10}
    };
    string[] knownDirections = { "left", "right", "up", "down" };
    string[] knownObjects = { "cube", "tile", "sphere", "cylinder", "pyramid", "cone", "prism" };
    string[] knownCommands = { "move", "start", "reset","done" };
    void Start()
    {
        originalCameraBackground = Camera.main.backgroundColor;
        turnCommands = new List<string>();
        if(EventHandler.Instance != null)
        {
            EventHandler.Instance.RegisterEvent("GameInteraction",ActionDecoder);
            EventHandler.Instance.RegisterEvent("ActionAck",ResponseAck);
            EventHandler.Instance.RegisterEvent("AutoDoneCheck",AutoDoneCheck);
        }
    }

    public void Update()
    {
        if(ExperimentManager.Instance.humanExperiment)
        {
            if(isPuzzleSolved)
            {
                Camera.main.backgroundColor = solvedCameraBackground;
            }
            else
            {
                Camera.main.backgroundColor = originalCameraBackground;
            }
        } 
    }
    public Tuple<string,string,string,string,int> decodeCommand(string command)
    {
        command = command.ToLower();
        string cmd = "";
        string foundObject = "";
        string foundObjectAttribute = "";
        string foundDirection = "";
        int repetition = 1; 
        // extacting command
        foreach (var obj in knownCommands)
        {
            if (command.Contains(obj))
            {
                cmd = obj;
                break;
            }
        }
        // extracting object name
        foreach (var obj in knownObjects)
        {
            if (command.Contains(obj))
            {
                foundObject = obj;
                break;
            }
        }
        // extracting object attribute
        if(foundObject != "")
        {
            string[] substrings = command.Split(" ");
            for(int index = 0; index < substrings.Length ; index++)
            {
                if(substrings[index] == foundObject)
                {
                    if(foundObject == "tile")
                    {
                        foundObjectAttribute = substrings[index+1];
                    }
                    else
                        foundObjectAttribute = substrings[index-1];
                }
            }
        }
        // extracting direction
        foreach (var obj in knownDirections)
        {
            if (command.Contains(obj))
            {
                foundDirection = obj;
                break;
            }
        }
        // extracting repetition
        if(foundObject != "tile")
        {
            Match match = Regex.Match(command, @"(\d+)");
            if (match.Success)
            {
                repetition = int.Parse(match.Value);
            }
            else
            {
                // If no digits found, try mapping words like "one", "two", "three" to numbers:
                
                foreach (var kvp in wordToNumber)
                {
                    if (command.Contains(kvp.Key))
                    {
                        repetition = kvp.Value;
                        break;
                    }
                }
            }
        }
        Tuple<string,string,string,string,int> decodedText = new Tuple<string,string,string,string,int>(cmd,foundObject,foundObjectAttribute,foundDirection,repetition);
        return decodedText;
    }
    // Update is called once per frame
    public void ActionDecoder(DataPacket data)
    {    
        turnCommands = data.messages;
        command_count++;
        
        foreach (string command in turnCommands)
        {
            Debugger.Instance.CreateNewAction();
            Debugger.Instance.SetCommandCount(command_count);       
            Debugger.Instance.Log("command is : " + command);
            Debugger.Instance.SetPrompt(command);
            action_count++;
            Debugger.Instance.SetActionCount(action_count);
            Tuple<string,string,string,string,int> decodedText = decodeCommand(command);
            Debug.LogWarning(decodedText);
            if(decodedText.Item1.Contains("move"))
            {
                
                Debug.Log("processing command Queue: " +command.ToString());
                
                string[] Tokens = command.Split(" ");
                //int id = Animator.StringToHash(Tokens[1] + " " + Tokens[2]);
                int id = 0;
                if(decodedText.Item2 == "tile")
                    id = Animator.StringToHash(decodedText.Item2 + " " + decodedText.Item3);
                else
                    id = Animator.StringToHash(decodedText.Item3 + " " + decodedText.Item2);
                if(!Debugger.Instance.isValidObject(id))
                {
                    if(decodedText.Item2 == "tile")
                        Debugger.Instance.SetValidity(decodedText.Item2 + " " + decodedText.Item3 + " is not a valid object");
                    else
                        Debugger.Instance.SetValidity(decodedText.Item3 + " " + decodedText.Item2 + " is not a valid object");
                }
                for(int i = 0 ; i < decodedText.Item5; i++)
                {
                    
                    EventHandler.Instance.InvokeCommand("move",id,decodedText.Item4);

                }               
            }
            else if(decodedText.Item1.Contains("start"))
            {
        
                EventHandler.Instance.InvokeCommand("init_target");
                Debugger.Instance.SetValidity("valid command. start of experiment");
            }
            else if(decodedText.Item1.Contains("done"))
            {
                recievedDoneCommand = true;
                isPuzzleSolved = true;
                GameObject[] targets = GameObject.FindGameObjectsWithTag("Commandable");
                Debugger.Instance.SetValidity("valid command. evaluating the board");
                foreach (GameObject target in targets)
                {
                    isPuzzleSolved  &= isPuzzleSolved &  target.GetComponent<TargetBehaviour>().evaluateGoal();
                }
                
            }
            else if(decodedText.Item1.Contains("reset"))
            {
                if(ExperimentManager.Instance.humanExperiment)
                    Debugger.Instance.RecordHumanLog();
                EmptyLog();
                ExperimentManager.Instance.Reset();
            }
            else
            {
                Debug.LogError(command);
                Debugger.Instance.SetValidity("not a legal command");
            }
        }
        EventHandler.Instance.InvokeCommand("capture_screenshot_for_ack"); 
         
    }
    public void AutoDoneCheck()
    {
        isPuzzleSolved = true;
        GameObject[] targets = GameObject.FindGameObjectsWithTag("Commandable");
        foreach (GameObject target in targets)
        {
            isPuzzleSolved  &= isPuzzleSolved &  target.GetComponent<TargetBehaviour>().evaluateGoal();
        }
    }
    public void ResponseAck(DataPacket response)
    {
        GameObject[] boardObjects = GameObject.FindGameObjectsWithTag("Commandable");
        foreach (GameObject boardObject in boardObjects)
        {
            string status = boardObject.GetComponent<TargetBehaviour>().getObjectChessStatus();
            ObjectData object_data =  boardObject.GetComponent<TargetBehaviour>().GetObjectData();
            Debugger.Instance.SetBoardStatus(status);
            Debugger.Instance.SetObjectData(object_data);
        }
        Debugger.Instance.SetGameStatus(isPuzzleSolved); 
        response.messages.Add(Debugger.Instance.GetJSONLog());
        Debug.Log(Debugger.Instance.GetJSONLog());
        if(ExperimentManager.Instance.humanExperiment)
        {
            response.data = Convert.FromBase64String("null");
            response.PrepareForSerialization();
        }
        if(recievedDoneCommand || ExperimentManager.Instance.loadedLandmarkData.auto_done_check)
        {
            recievedDoneCommand = false;
            if(isPuzzleSolved)
            {
                Debugger.Instance.SetValidity("Puzzle is soveled correctly");
                if(!ExperimentManager.Instance.humanExperiment)
                    NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(response));
                else
                {
                    InteractionUI.Instance.saveActionAck(JsonUtility.ToJson(response));
                    Debugger.Instance.RecordHumanLog();
                }
                    
                EmptyLog();
                ExperimentManager.Instance.Reset();
                return;
            }
            else
            {
                if(!ExperimentManager.Instance.loadedLandmarkData.auto_done_check)
                    Debugger.Instance.SetValidity("Puzzle is not solved correctly, try again");
            }
        }
        if(!InteractionUI.Instance.IsHumanExperiment())
            NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(response));
        else
        {
            if(!ExperimentManager.Instance.loadedLandmarkData.auto_done_check)
                InteractionUI.Instance.saveActionAck(JsonUtility.ToJson(response));
        }
        EmptyLog();
            

    }
    public void EmptyLog()
    {
        if(Debugger.Instance != null)
            Debugger.Instance.ClearLogs();
        turnCommands.Clear();
    }
    private void OnDestroy()
    {
        if(EventHandler.Instance != null)
        {
            EventHandler.Instance.UnregisterEvent("GameInteraction",ActionDecoder);
            EventHandler.Instance.UnregisterEvent("ActionAck",ResponseAck);
            EventHandler.Instance.UnregisterEvent("AutoDoneCheck",AutoDoneCheck);
        }
          
    }
}
