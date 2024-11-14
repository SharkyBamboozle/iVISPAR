using System.Collections;
using System.Collections.Generic;
using System.Net.Sockets;
using UnityEngine;
using UnityEngine.SceneManagement;


public class ExperimentManager2 : MonoBehaviour
{
    // Start is called before the first frame update
    public static ExperimentManager2 Instance { get; private set; }
    
    public List<string> objectType;
    //make variables for yaml file
    private string experimentType = "maze";
    void Awake()
    {
        if (Instance != null && Instance != this) 
        { 
            Destroy(this); 
        } 
        else 
        { 
            Instance = this; 
            DontDestroyOnLoad(gameObject);
        } 
    }
    void Start()
    {
        
        SceneManager.LoadScene(experimentType, LoadSceneMode.Single);
        
    }
    // Update is called once per frame
}



