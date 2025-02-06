using System.Collections.Generic;
using JetBrains.Annotations;
using UnityEngine.Networking;
using UnityEngine;
using UnityEngine.SceneManagement;
using System.Collections;
using System.Linq;
using System.Runtime.InteropServices;
public class ExperimentManager : MonoBehaviour
{
    public static ExperimentManager Instance { get; private set; }
    [DllImport("__Internal")]
    private static extern string GetQueryString();
    [DllImport("__Internal")]
    private static extern void DownloadFile(string filename, string content);
    public LandmarkData loadedLandmarkData;
    //private string experimentType = "puzzle";  // Default experiment type
    //public string serverAdress =  "ws://localhost:1984";
    public string url = "localhost";
    public string socketPort = "1984";
    public bool isConnected = false;
    public bool humanExperiment = false;
    private string configPort = "400";
    private string configURL = "localhost:400";
    private Queue<string> configFiles; 

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
        loadedLandmarkData = new LandmarkData();
         SceneManager.LoadScene("Main", LoadSceneMode.Single);
        if(this.humanExperiment)
        {
            InteractionUI.Instance.isLevelLoaded = false;
            LoadHumanExperiment();
        }
        
    }
    void Start()
    {
        // Load the scene after the configuration has been loaded
        //SceneManager.LoadScene(experimentType, LoadSceneMode.Single);
        // connect to server
    #if UNITY_WEBGL && !UNITY_EDITOR 
        string queryString = GetQueryString();
        var parameters = ParseQueryString(queryString);
        if(parameters.ContainsKey("human"))
        {
            if(parameters["human"] == "true")
                humanExperiment = true;
            if(url != "localhost")
            {
                configURL = string.Format("https://{0}:{1}/",url,configPort);
                Debug.LogFormat("Config url is {0}",configURL);
            }


        }
    #endif
        EventHandler.Instance.RegisterEvent("Setup",SetupExperiment);
        string serverAddress = "";
        if(url == "localhost")
        {
            serverAddress = string.Format("ws://{0}:{1}",url,socketPort);
        }
        else
        {
            serverAddress = string.Format("wss://{0}:{1}",url,socketPort);
            configURL = string.Format("https://{0}:{1}/",url,configPort);
            Debug.LogFormat("Config url is {0}",configURL);
        }
        if(!humanExperiment)
            NetworkManger.Instance.ConnectToServer(serverAddress);
        else
        {
            InteractionUI.Instance.isHumanExperiment = true;
            //StartCoroutine("DownloadAvailbleList");
        }
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
    public IEnumerator DownloadAvailbleList()
    {
        string url = configURL + "Available.txt";
        Debug.Log($"Downloading JSON file from: {url}");

        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError($"Error downloading file: {request.error}");
        }
        else
        {
            // Get the content of the file as a string
            string cofigFilesList = request.downloadHandler.text;
            configFiles = new Queue<string>(cofigFilesList.Split("\n"));
            Debug.Log($"there are {configFiles.Count} configs available");

            // Parse the JSON (example)
        }
    }
    public void SetConfigList(string rawList)
    {
        if(rawList != "")
        {      
            //configFiles = rawList.Split("\n").ToList();
            configFiles = new Queue<string>(rawList.Split("\n"));
            Debug.Log($"there are {configFiles.Count} configs available");
            LoadHumanExperiment();
        }
    }
    
    public void LoadHumanExperiment()
    {
        if(configFiles.Count != 0)
        {   string file = configFiles.Dequeue();
            
            StartCoroutine(DownloadConfig(file));
        }
        else
        {
            EventHandler.Instance.InvokeCommand("EndExperiment");
            string fileName = "experiment_log.json";
            List<string> logs = InteractionUI.Instance.getLog();
            string logContent = "[";
            int counter = 0;
            foreach(string log in logs)
            {
                if(counter < logs.Count)
                    logContent = logContent + log +  "\n , ";
                else
                    logContent = logContent + log +  "\n";
                counter++;
            }
            logContent = logContent + "]";
            Debug.Log(logContent);
            DownloadFile(fileName, logContent);
            
        }
        
    }
    public void Download()
    {
        string fileName = "experiment_log.json";
        List<string> logs = InteractionUI.Instance.getLog();
        string logContent = "[";
        int counter = 0;
        foreach(string log in logs)
        {
            if(counter < logs.Count -1)
                logContent = logContent + log +  "\n , ";
            else
                logContent = logContent + log +  "\n";
            counter++;
        }
        logContent = logContent + "]";
        Debug.Log(logContent);
        DownloadFile(fileName, logContent);
    }
    public IEnumerator DownloadConfig(string config)
    {
        string url = configURL + config;
        Debug.Log($"Downloading JSON file from: {url}");

        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
        {
            Debug.LogError($"Error downloading file: {request.error}");
        }
        else
        {
            // Get the content of the file as a string
            string setupContent = request.downloadHandler.text;
            Debug.Log($"got confog {setupContent} configs available");
            DataPacket data = new DataPacket();
            data.command = "Setup";
            data.messages.Add(setupContent);
            EventHandler.Instance.InvokeCommand("Setup",data);
            
        }
    }
    private static System.Collections.Generic.Dictionary<string, string> ParseQueryString(string query)
    {
        var dict = new System.Collections.Generic.Dictionary<string, string>();

        if (string.IsNullOrEmpty(query) || !query.Contains("="))
            return dict;

        // Remove the "?" at the start of the query string
        if (query.StartsWith("?"))
            query = query.Substring(1);

        // Split key-value pairs
        var pairs = query.Split('&');
        foreach (var pair in pairs)
        {
            var keyValue = pair.Split('=');
            if (keyValue.Length == 2)
            {
                var key = System.Uri.UnescapeDataString(keyValue[0]);
                var value = System.Uri.UnescapeDataString(keyValue[1]);
                dict[key] = value;
            }
        }

        return dict;
    }
    
}
