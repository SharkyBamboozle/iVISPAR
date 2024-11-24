using System.Collections.Generic;
using JetBrains.Annotations;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;
public class ExperimentManager : MonoBehaviour
{
    public static ExperimentManager Instance { get; private set; }
    
    public LandmarkData loadedLandmarkData;
    //private string experimentType = "puzzle";  // Default experiment type
    //public string serverAdress =  "ws://localhost:1984";
    public string url = "localhost";
    public string socketPort = "1984";
    public bool isConnected = false;
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
            DontDestroyOnLoad(gameObject);  // Persist this object across scenes
        }

        // Load the configuration using ConfigLoader
        Screen.SetResolution(800,600,true);
        
    }
    public void Reset() {
         SceneManager.LoadScene("Main", LoadSceneMode.Single);
    }
    void Start()
    {
        // Load the scene after the configuration has been loaded
        //SceneManager.LoadScene(experimentType, LoadSceneMode.Single);
        // connect to server 
        EventHandler.Instance.RegisterEvent("Setup",SetupExperiment);
        string serverAddress = string.Format("ws://{0}:{1}",url,socketPort);
        NetworkManger.Instance.ConnectToServer(serverAddress);
    }
    public void SetupExperiment(DataPacket setup_data)
    {
        Debug.LogFormat("setup command recieved from {0}, processing do load...",setup_data.from);
        List<string> configDatas = setup_data.messages;
        Debug.Log(configDatas);
        Deserialize(configDatas[0]);
        SceneManager.LoadScene(loadedLandmarkData.experiment_type, LoadSceneMode.Single);
    }
    // Public getter for landmark data
    public void Deserialize(string config)
    {
        
        try
        {
            loadedLandmarkData = JsonUtility.FromJson<LandmarkData>(config);
            // uncommnet this later after the refavtor
            //Screen.SetResolution(loadedLandmarkData.width, loadedLandmarkData.height,false);
        }
        catch
        {
            Debug.LogError("Can't read config file. Maybe you have forgotten one!");
        }

        // Example: You can now access the data in loadedLandmarkData
        if (loadedLandmarkData != null)
        {
            Debug.Log($"Experiment ID: {loadedLandmarkData.experiment_id}");
            Debug.Log($"Number of landmarks: {loadedLandmarkData.landmarks.Length}");
        }
        else
            Debug.LogError("Problem reading config file!");
    }
}
