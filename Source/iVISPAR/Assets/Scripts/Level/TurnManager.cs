using System;
using System.Collections;
using System.Collections.Generic;
using System.Runtime.ExceptionServices;
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
        
        foreach (string command in turnCommands)
        {
            Debugger.Instance.Log("command is : " + command);
            if(command.Contains("move"))
            {
                Debug.Log("processing command Queue: " +command.ToString());
                string[] Tokens = command.Split(" ");
                int id = Animator.StringToHash(Tokens[1] + " " + Tokens[2]);
                if(!Debugger.Instance.isValidObject(id))
                {
                    Debugger.Instance.AppendLastLog(" - " + Tokens[1] + " " + Tokens[2] + " is not a valid object");
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
            if(command.Contains("start"))
            {
        
                EventHandler.Instance.InvokeCommand("init_target");
            }
            if(command.Contains("done"))
            {
                recievedDoneCommand = true;
                isPuzzleSolved = true;
                GameObject[] targets = GameObject.FindGameObjectsWithTag("Commandable");
                foreach (GameObject target in targets)
                {
                    isPuzzleSolved  &= isPuzzleSolved &  target.GetComponent<TargetBehaviour>().evaluateGoal();
                }
                
            }
            else
            {
                Debugger.Instance.AppendLastLog(" - is not a legal command");
            }
            if(command.Contains("reset"))
            {
                ExperimentManager.Instance.Reset();
            }
        }
        EventHandler.Instance.InvokeCommand("capture_screenshot_for_ack"); 
    }
    public void ResponseAck(DataPacket response)
    {
        GameObject[] boardObjects = GameObject.FindGameObjectsWithTag("Commandable");
        foreach (GameObject boardObject in boardObjects)
        {
            response.messages.Add(boardObject.GetComponent<TargetBehaviour>().getObjectStatus());
        }
        response.messages.AddRange(Debugger.Instance.getLogs());
        if(recievedDoneCommand)
        {
            recievedDoneCommand = false;
            if(isPuzzleSolved)
            {
                response.messages.Insert(0,"Puzzle is soveled correctly");
                NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(response));
                EmptyLog();
                ExperimentManager.Instance.Reset();
            }
            else
            {
                response.messages.Insert(0,"Puzzle is not solved correctly, try again");
            }
        }
        NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(response));
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
