using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Security.Cryptography;
using JetBrains.Annotations;
using UnityEngine;

public class Debugger : MonoBehaviour
{
    public static Debugger Instance { get; private set; }
    public Dictionary<int,string> objectList;
    public List<string> logs;

    public EventLogs jsonLogs;
    public List<EventLogs> humanExperimentLogs;
    void Start()
    {
        
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
            objectList = new Dictionary<int, string>();
            logs = new List<string>();
            jsonLogs = new EventLogs();
            humanExperimentLogs = new List<EventLogs>();
            DontDestroyOnLoad(gameObject);  // Persist this object across scenes
        }
        
    }
    // Update is called once per frame
    void Update()
    {
        
    }
    public void ClearObjectList()
    {
        objectList.Clear();
    }
    public void ClearLogs()
    {
        
        logs.Clear();
        jsonLogs = new EventLogs();
    }
    public void Log(string message)
    {
        logs.Add(message);
    }
    public void AppendLastLog(string message)
    {
        logs[logs.Count -1] = logs[logs.Count -1] + message;
    }
    public List<string> getLogs()
    {
        return logs;
    }
    public bool isValidObject(int objectID)
    {
        return objectList.ContainsKey(objectID);
    }
    public void CreateNewAction()
    {
        jsonLogs.Actions.Add(new NetAction());
    }
    public void SetCommandCount(int count)
    {
        //jsonLogs.Actions.Last<NetAction>().command_count = count;
        jsonLogs.Actions[jsonLogs.Actions.Count -1].command_count = count;
    }
    public void SetActionCount(int count)
    {
        jsonLogs.Actions[jsonLogs.Actions.Count -1].action_count = count;
    }
    public void SetPrompt(string prompt)
    {
        jsonLogs.Actions[jsonLogs.Actions.Count -1].prompt = prompt;
    }
    public void SetValidity(string validity)
    {
        jsonLogs.Actions[jsonLogs.Actions.Count -1].valididy.Add(validity);
    }
    public void SetBoardStatus(string boardStatus)
    {
        jsonLogs.board_state.Add(boardStatus);
    }
    public void SetObjectData(ObjectData status)
    {
        jsonLogs.board_data.Add(status);
    }
    public void SetGameStatus(bool isGameDone)
    {
        jsonLogs.game_done = isGameDone;
    }
    public string GetJSONLog()
    {
        return JsonUtility.ToJson(jsonLogs);
    }
    public void RecordHumanLog()
    {
        humanExperimentLogs.Add(jsonLogs);
    }

}
