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
    private List<string> log;
    private List<string> turnCommands;
    void Start()
    {
        log = new List<string>();
        turnCommands = new List<string>();
        EventHandler.Instance.RegisterEvent("GameInteraction",ActionDecoder);
        EventHandler.Instance.RegisterEvent("ActionAck",ResponseAck);
        EventHandler.Instance.RegisterEvent("LegalMove",LegalMove);
        EventHandler.Instance.RegisterEvent("IlegalMove",IlegalMove);
    }
    
    // Update is called once per frame
    public void ActionDecoder(DataPacket data)
    {    
        turnCommands = data.messages;
        foreach (string command in turnCommands)
        {
            if(command.Contains("move"))
            {
                Debug.Log("processing command Queue: " +command.ToString());
                string[] Tokens = command.Split(" ");
                int id = Animator.StringToHash(Tokens[1] + " " + Tokens[2]);
                int repetition = 1;
                if(Tokens.Length > 4)
                {
                    try
                    {
                        repetition = int.Parse(Tokens[4]);
                    }
                    catch(Exception ex)
                    {
                        Debug.LogError("tocken not an intiger");
                    }
                }
                for(int i = 0 ; i < repetition; i++)
                    EventHandler.Instance.InvokeCommand("move",id,Tokens[3]);
                                 
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
        //for(int index= 0; index < log.Count ; index++)
        //    turnCommands[index] = string.Format("{0} {1} action",turnCommands[index],log[index]);
        response.messages.AddRange(log);
        NetworkManger.Instance.SendWebSocketMessage(JsonUtility.ToJson(response));
        EmptyLog();
    }
    public void LegalMove()
    {
        log.Add("was a Legal");
    }
    public void IlegalMove()
    {
        log.Add("was not a Legal move");
    }
    public void EmptyLog()
    {
        log.Clear();
        turnCommands.Clear();
    }
}
