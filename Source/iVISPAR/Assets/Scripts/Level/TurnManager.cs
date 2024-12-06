using System;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.ExceptionServices;
using Unity.VisualScripting;
using Unity.VisualScripting.Antlr3.Runtime;
using UnityEngine;

public class TurnManager : MonoBehaviour
{
    // Start is called before the first frame update
    bool initialized = false;
    //private List<string> log;
    private List<string> turnCommands;
    int currentCommand = 0;
    bool isPuzzleSolved = false;
    bool recievedDoneCommand = false;
    private int command_count = 0;
    private int action_count = 0;
    void Start()
    {
        turnCommands = new List<string>();
        if(EventHandler.Instance != null)
        {
            EventHandler.Instance.RegisterEvent("GameInteraction",ActionDecoder);
            EventHandler.Instance.RegisterEvent("ActionAck",ResponseAck);
        }
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
            if(command.Contains("move"))
            {
                
                Debug.Log("processing command Queue: " +command.ToString());
                string[] Tokens = command.Split(" ");
                int id = Animator.StringToHash(Tokens[1] + " " + Tokens[2]);
                if(!Debugger.Instance.isValidObject(id))
                {
                    Debugger.Instance.SetValidity("Tokens[1]" + " " + Tokens[2] + " is not a valid object");
                }
                int repetition = 1;
                if(Tokens.Length > 4)
                {
                    try
                    {
                        repetition = int.Parse(Tokens[4]);
                    }
                    catch(Exception ex)
                    {
                        Debug.LogError("tocken not an intiger. Error " + ex.Message);

                    }
                }
                for(int i = 0 ; i < repetition; i++)
                {
                    
                    EventHandler.Instance.InvokeCommand("move",id,Tokens[3]);

                }               
            }
            else if(command.Contains("start"))
            {
        
                EventHandler.Instance.InvokeCommand("init_target");
                Debugger.Instance.SetValidity("valid command. start of experiment");
            }
            else if(command.Contains("done"))
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
            else if(command.Contains("reset"))
            {
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
    public void ResponseAck(DataPacket response)
    {
        GameObject[] boardObjects = GameObject.FindGameObjectsWithTag("Commandable");
        foreach (GameObject boardObject in boardObjects)
        {
            string status = boardObject.GetComponent<TargetBehaviour>().getObjectChessStatus();
            //response.messages.Add(status);
            Debugger.Instance.SetBoardStatus(status);
        }
        Debugger.Instance.SetGameStatus(isPuzzleSolved);
        //response.messages.AddRange(Debugger.Instance.getLogs());
        response.messages.Add(Debugger.Instance.GetJSONLog());
        Debug.Log(Debugger.Instance.GetJSONLog());
        if(recievedDoneCommand)
        {
            recievedDoneCommand = false;
            if(isPuzzleSolved)
            {
                Debugger.Instance.SetValidity("Puzzle is soveled correctly");
                if(!InteractionUI.Instance.IsHumanExperiment())
                    NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(response));
                else
                {
                    InteractionUI.Instance.saveActionAck(JsonUtility.ToJson(response));
                }
                EmptyLog();
                ExperimentManager.Instance.Reset();
                return;
            }
            else
            {
                Debugger.Instance.SetValidity("Puzzle is not solved correctly, try again");
            }
        }
        if(!InteractionUI.Instance.IsHumanExperiment())
            NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(response));
        else
        {
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
        }
          
    }
}
