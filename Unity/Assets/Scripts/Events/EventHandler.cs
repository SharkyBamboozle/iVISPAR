using System.Collections;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using Unity.VisualScripting.Dependencies.NCalc;
using UnityEngine;
using UnityEngine.Events;

public class EventHandler : MonoBehaviour
{
    public static EventHandler Instance { get; private set; }
    public Dictionary<string,UnityEvent<DataPacket>> eventRegistery;
    public Dictionary<string,UnityEvent> internalEventRegistery;
    public Dictionary<string,UnityEvent<int,string>> actionEventRegistery;
    
    // Start is called before the first frame update
    void Awake()
    {
        // Singleton pattern
        if (Instance != null && Instance != this) 
        { 
            Destroy(this); 
        } 
        else 
        { 
            eventRegistery = new Dictionary<string, UnityEvent<DataPacket>>();
            internalEventRegistery = new Dictionary<string, UnityEvent>();
            actionEventRegistery = new Dictionary<string, UnityEvent<int, string>>();
            Instance = this; 
            DontDestroyOnLoad(gameObject);  // Persist this object across scenes
        }    
    }
    public bool RegisterEvent(string command, UnityAction<DataPacket> callback)
    {
        if (eventRegistery != null)
        {
            if(eventRegistery.ContainsKey(command))
            {
                eventRegistery[command].AddListener(callback);
                return true;
            }
            else
            {
                eventRegistery.Add(command,new UnityEvent<DataPacket>());
                eventRegistery[command].AddListener(callback);
                return true;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool RegisterEvent(string command, UnityAction callback)
    {
        if (internalEventRegistery != null)
        {
            if(internalEventRegistery.ContainsKey(command))
            {
                internalEventRegistery[command].AddListener(callback);
                return true;
            }
            else
            {
                internalEventRegistery.Add(command,new UnityEvent());
                internalEventRegistery[command].AddListener(callback);
                return true;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool RegisterEvent(string command, UnityAction<int,string> callback)
    {
        if (actionEventRegistery != null)
        {
            if(actionEventRegistery.ContainsKey(command))
            {
                actionEventRegistery[command].AddListener(callback);
                return true;
            }
            else
            {
                actionEventRegistery.Add(command,new UnityEvent<int,string>());
                actionEventRegistery[command].AddListener(callback);
                return true;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool UnregisterEvent(string command, UnityAction<DataPacket> callback)
    {
        if (eventRegistery != null)
        {
            if(eventRegistery.ContainsKey(command))
            {
                eventRegistery[command].RemoveAllListeners();
                return true;
            }
            else
            {
                 Debug.LogFormat("no command {0} has been registed with event handler",command);
                return false;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool UnregisterEvent(string command, UnityAction<int,string> callback)
    {
        if (actionEventRegistery != null)
        {
            if(actionEventRegistery.ContainsKey(command))
            {
                actionEventRegistery[command].RemoveAllListeners();
                return true;
            }
            else
            {
                 Debug.LogFormat("no command {0} has been registed with event handler",command);
                return false;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool UnregisterEvent(string command, UnityAction callback)
    {
        if (internalEventRegistery != null)
        {
            if(internalEventRegistery.ContainsKey(command))
            {
                internalEventRegistery[command].RemoveAllListeners();
                return true;
            }
            else
            {
                 Debug.LogFormat("no command {0} has been registed with event handler",command);
                return false;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool InvokeCommand(string command, DataPacket data)
    {
        if (eventRegistery != null)
        {
            if(eventRegistery.ContainsKey(command))
            {
                eventRegistery[command]?.Invoke(data);
                return true;
            }
            else
            {
                Debug.LogFormat("no command {0} has been registed with event handler",command);
                return false;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool InvokeCommand(string command,int objectID, string message)
    {
        if (actionEventRegistery != null)
        {
            if(actionEventRegistery.ContainsKey(command))
            {
                actionEventRegistery[command]?.Invoke(objectID,message);
                return true;
            }
            else
            {
                Debug.LogFormat("no command {0} has been registed with event handler",command);
                return false;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    public bool InvokeCommand(string command)
    {
        if (internalEventRegistery != null)
        {
            if(internalEventRegistery.ContainsKey(command))
            {
                internalEventRegistery[command]?.Invoke();
                return true;
            }
            else
            {
                Debug.LogFormat("no command {0} has been registed with event handler",command);
                return false;
            }
            
        }
        else
        {
            Debug.LogError("Event registary not initialized yet!");
            return false;
        }
    }
    // Update is called once per frame
    private void OnDestroy() {
        
    }
}
