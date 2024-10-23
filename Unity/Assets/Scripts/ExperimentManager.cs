using UnityEngine;
using UnityEngine.SceneManagement;

public class ExperimentManager : MonoBehaviour
{
    public static ExperimentManager Instance { get; private set; }
    
    private ConfigLoader configLoader;
    private string experimentType = "puzzle";  // Default experiment type

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
        configLoader = gameObject.AddComponent<ConfigLoader>();
        configLoader.LoadConfig();
    }

    void Start()
    {
        // Load the scene after the configuration has been loaded
        SceneManager.LoadScene(experimentType, LoadSceneMode.Single);
    }

    // Public getter for landmark data
    public LandmarkData GetLandmarkData()
    {
        return configLoader.loadedLandmarkData;
    }
}
