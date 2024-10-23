using System;
using System.IO;
using UnityEngine;

public class ConfigLoader : MonoBehaviour
{
    public LandmarkData loadedLandmarkData;
    public string jsonFileName = "puzzle.json";  // Without the .json extension
    
#if UNITY_EDITOR
    public string path = "Assets/Resources/";
#else
    public string path = "/Resources/";
#endif

    // Method to load the JSON data
    public void LoadConfig()
    {
        
        string full_path = "";

#if UNITY_EDITOR
        full_path = path + jsonFileName;
#else
        full_path = Application.dataPath + path + jsonFileName;
#endif

        try
        {
        loadedLandmarkData = JsonUtility.FromJson<LandmarkData>(File.ReadAllText(full_path));
        }
        catch(Exception e)
        {
            Debug.LogError("Can't read config file. Maybe you have forgotten one!");
        }
        //TextAsset jsonFile 
        //Resources.Load<TextAsset>(jsonFileName);
        // if (jsonFile != null)
        // {
        //     loadedLandmarkData = JsonUtility.FromJson<LandmarkData>(jsonFile.text);
        //     Debug.Log("JSON data loaded successfully!");
        // }
        // else
        // {
        //     Debug.LogError("Failed to load JSON file from Resources.");
        // }

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
