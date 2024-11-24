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

}
