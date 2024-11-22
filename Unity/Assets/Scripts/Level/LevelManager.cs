using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LevelManager : MonoBehaviour
{
    public List<Material> objectMaterials;  // List of possible materials for objects
    
    private (int, int) gridSize;
    private List<GameObject> landmarks = new List<GameObject>();

    public GameObject Pyramid;
    [Range(0f,1f)]
    public float metallic = 0.7f;
    [Range(0f,1f)]
    public float smoothness = 0.7f;

    public Texture2D albedoTexture; 
    public Texture2D normalTexture;
    public float normalScale = 1; 

    public Texture2D heightMap;
    public float heightScale = 1; 

    void Start() 
    {
        // Get the config data from ExperimentManager
        if(ExperimentManager.Instance != null)
        {
            LandmarkData landmarkData = ExperimentManager.Instance.loadedLandmarkData;  // Use the shared class

            if (landmarkData != null)
            {
                // Retrieve the config data
                gridSize = (landmarkData.grid_size, landmarkData.grid_size);
                
                // Set grid size (if you have a grid-based system)
                // Create landmarks based on the config data
                Debug.Log(landmarkData.landmarks);
                CreateLandmarks(landmarkData.landmarks);
            }
            else
            {
                Debug.LogError("Failed to load config data from ExperimentManager.");
            }
        }
    }

    void CreateLandmarks(Landmark[] landmarksData)
    {
        // Get the reference to the GridBoard (assuming there's only one GridBoard object in the scene)
        GridBoard gridBoard = GameObject.FindGameObjectsWithTag("Grids")[0].GetComponent<GridBoard>();


        foreach (var landmark in landmarksData)
        {
            GameObject obj = null;
            // Determine the object type (cube, ball, capsule, etc.)
            switch (landmark.body.ToLower())
            {
                case "cube":
                    obj = GameObject.CreatePrimitive(PrimitiveType.Cube);
                    break;
                case "sphere":
                    obj = GameObject.CreatePrimitive(PrimitiveType.Sphere);
                    break;
                case "pyramid":
                    if(Pyramid != null)
                        obj = GameObject.Instantiate(Pyramid);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                default:
                    Debug.LogError($"Unknown object type: {landmark.body}");
                    continue;
            }

            // Use the 'coordinate' array to set the object's position
            int gridX = (int)landmark.goal_coordinate[0];
            int gridZ = (int)landmark.goal_coordinate[1];
            obj.transform.position = new Vector3(gridX, 0, gridZ);
            obj.transform.rotation = Quaternion.identity;
            obj.tag = "Commandable";  // Example tag for interactable objects
            obj.AddComponent<TargetBehaviour>();  // Assuming you have this script
            obj.GetComponent<TargetBehaviour>().SetInfo(landmark.body.ToLower(),landmark.color);
            // Set object color based on the 'color' property in the landmark data
            Material mat = new Material(Shader.Find("Standard"));
            Color objectColor;
            if (ColorUtility.TryParseHtmlString(landmark.color, out objectColor))
            {
                // Set the color of the object's material
                mat.SetFloat("_Metallic",metallic);
                mat.SetFloat("_Glossiness",smoothness);
                if( albedoTexture != null )
                    mat.SetTexture("_MainTex",albedoTexture);
                if( normalTexture != null )
                    mat.SetTexture("_BumpMap",normalTexture);
                    mat.SetFloat("_BumpScale",normalScale);
                if( heightMap != null )
                    mat.SetTexture("_ParallaxMap",heightMap);
                    mat.SetFloat("__Parallax",heightScale);

                mat.color = objectColor;
                obj.GetComponent<Renderer>().material = mat;
            }
            else
            {
                Debug.LogWarning($"Invalid color: {landmark.color}, setting to magenta.");
                mat.color = Color.magenta;  // Default color if the color string is invalid
                obj.GetComponent<Renderer>().material = mat;
            }

            // Assuming TargetBehaviour is a script that manages positioning on a grid
            TargetBehaviour targetBehaviour = obj.GetComponent<TargetBehaviour>();
            // Assign the same GridBoard reference that LevelManager uses
            targetBehaviour.setPositionOnGrid((int)landmark.goal_coordinate[0], (int)landmark.goal_coordinate[1]);
            targetBehaviour.setGoalPos((int)landmark.goal_coordinate[0], (int)landmark.goal_coordinate[1]);
            targetBehaviour.setStartPos((int)landmark.start_coordinate[0], (int)landmark.start_coordinate[1]);

            int objectID = Animator.StringToHash(landmark.color.ToLower() + " " + landmark.body.ToLower());
            targetBehaviour.SetID(objectID);

            // Set grid occupancy for this object using the GridBoard
            if (gridBoard != null)
            {
            //    gridBoard.setOccupancy(gridX, gridZ, true); // Mark the grid cell as occupied
                if (gridBoard.GetOccupany(gridX, gridZ) == true)
                {   
                    Debug.LogError("Object was set on occupied position, probably error in config json file");
                }

            }
        }
        StartLevel();
    }

    public void StartLevel()
    {
        EventHandler.Instance.InvokeCommand("capture_send_screenshot");
        //EventHandler.Instance.InvokeCommand("init_target");
    }
}
