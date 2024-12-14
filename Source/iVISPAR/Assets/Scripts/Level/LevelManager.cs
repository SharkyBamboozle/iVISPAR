using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class LevelManager : MonoBehaviour
{
    public List<Material> objectMaterials;  // List of possible materials for objects
    
    //private (int, int) gridSize;
    private List<GameObject> landmarks = new List<GameObject>();
    public GameObject Cube;
    public GameObject Sphere;
    public GameObject Pyramid;
    public GameObject Cylinder;
    public GameObject Cone;
    public GameObject Prism;
    public GameObject Tile;
    public float hedronOffset = -0.2f;
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
                //gridSize = (landmarkData.grid_size, landmarkData.grid_size);
                
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
        Debug.Log("setting up the Scene");
        // Get the reference to the GridBoard (assuming there's only one GridBoard object in the scene)
        GridBoard gridBoard = GameObject.FindGameObjectsWithTag("Grids")[0].GetComponent<GridBoard>();


        foreach (var landmark in landmarksData)
        {
            GameObject obj = null;
            int gridX = (int)landmark.goal_coordinate[0];
            int gridZ = (int)landmark.goal_coordinate[1];
            // Determine the object type (cube, ball, capsule, etc.)
            switch (landmark.body.ToLower())
            {
                case "cube":
                    if(Cube != null)
                        obj = GameObject.Instantiate(Cube);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                case "sphere":
                    if(Sphere != null)
                        obj = GameObject.Instantiate(Sphere);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                case "cylinder":
                    if(Cylinder != null)
                        obj = GameObject.Instantiate(Cylinder);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                case "pyramid":
                    if(Pyramid != null)
                        obj = GameObject.Instantiate(Pyramid);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                case "cone":
                    if(Cone != null)
                        obj = GameObject.Instantiate(Cone);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                case "prism":
                    if(Prism != null)
                        obj = GameObject.Instantiate(Prism);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                case "tile":
                    if(Prism != null)
                        obj = GameObject.Instantiate(Tile);
                    else
                        obj = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                    break;
                default:
                    Debug.LogError($"Unknown object type: {landmark.body}");
                    continue;
            }

            // Use the 'coordinate' array to set the object's position
            obj.transform.position = new Vector3(gridX, 0, gridZ);   
            obj.transform.rotation = Quaternion.identity;
            obj.tag = "Commandable";  // Example tag for interactable objects
            obj.AddComponent<TargetBehaviour>();  // Assuming you have this script
            obj.GetComponent<TargetBehaviour>().SetInfo(landmark.body.ToLower(),landmark.color, landmark.geom_nr);
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
            if(!ExperimentManager.Instance.loadedLandmarkData.use_rendering)
            {
                obj.GetComponent<MeshRenderer>().enabled = false;
            }
            TargetBehaviour targetBehaviour = obj.GetComponent<TargetBehaviour>();
            // Assign the same GridBoard reference that LevelManager uses
            targetBehaviour.setPositionOnGrid((int)landmark.goal_coordinate[0], (int)landmark.goal_coordinate[1]);
            targetBehaviour.setGoalPos((int)landmark.goal_coordinate[0], (int)landmark.goal_coordinate[1]);
            targetBehaviour.setStartPos((int)landmark.start_coordinate[0], (int)landmark.start_coordinate[1]);
            if(landmark.body.ToLower() == "tile")
            {
                int objectID = Animator.StringToHash(landmark.body.ToLower() + " " + landmark.geom_nr.ToLower());
                Debugger.Instance.objectList.Add(objectID, landmark.body.ToLower() + " " + landmark.geom_nr.ToLower());
                targetBehaviour.SetID(objectID);
            }
            else
            {
                int objectID = Animator.StringToHash(landmark.color.ToLower() + " " + landmark.body.ToLower());
                Debugger.Instance.objectList.Add(objectID, landmark.color.ToLower() + " " + landmark.body.ToLower());
                targetBehaviour.SetID(objectID);
            }
                

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
        
        if(InteractionUI.Instance.IsHumanExperiment())
            InteractionUI.Instance.isLevelLoaded = true;

        EventHandler.Instance.InvokeCommand("capture_send_screenshot");
    }
    private void OnDestroy() {
        if(Debugger.Instance != null)
            Debugger.Instance.ClearObjectList();
    }
}
