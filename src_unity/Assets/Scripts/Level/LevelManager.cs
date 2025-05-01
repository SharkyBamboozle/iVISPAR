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
    public GameObject Diamond;
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
    public Dictionary<int,Vector3> orientationMap;
    public Dictionary<int,Dictionary<string,int>> flipTransitionMap;
    void Start() 
    {
        // Get the config data from ExperimentManager
        orientationMap = new Dictionary<int, Vector3>(){
            {1 , new Vector3(0f,0f,0f)},
            {2 , new Vector3(0f,90f,0f)},
            {3 , new Vector3(0f,180f,0f)},
            {4 , new Vector3(0f,270f,0f)},
            {5 , new Vector3(270f,180f,180f)},
            {6 , new Vector3(270f,180f,270f)},
            {7 , new Vector3(270f,180f,0f)},
            {8 , new Vector3(270f,180f,90f)},
            {9 , new Vector3(0,90f,270f)},
            {10 , new Vector3(0,180f,270f)},
            {11 , new Vector3(0,270f,270f)},
            {12 , new Vector3(0,0f,270f)}
        };
        

        flipTransitionMap = new Dictionary<int, Dictionary<string, int>>{
            {1 , new Dictionary<string, int>{{"left",8} , {"right",12} , {"up",9}, {"down",5}} },
            {2 , new Dictionary<string, int>{{"left",6} , {"right",10} , {"up",5}, {"down",9}} },
            {3 , new Dictionary<string, int>{{"left",10} , {"right",6} , {"up",7}, {"down",11}} },
            {4 , new Dictionary<string, int>{{"left",12} , {"right",8} , {"up",11}, {"down",7}} },
            {5 , new Dictionary<string, int>{{"left",7} , {"right",9} , {"up",1}, {"down",2}} },
            {6 , new Dictionary<string, int>{{"left",3} , {"right",2} , {"up",8}, {"down",10}} },
            {7 , new Dictionary<string, int>{{"left",11} , {"right",5} , {"up",4}, {"down",3}} },
            {8 , new Dictionary<string, int>{{"left",4} , {"right",1} , {"up",12}, {"down",6}} },
            {9 , new Dictionary<string, int>{{"left",5} , {"right",11} , {"up",2}, {"down",1}} },
            {10 , new Dictionary<string, int>{{"left",2} , {"right",3} , {"up",6}, {"down",12}} },
            {11 , new Dictionary<string, int>{{"left",9} , {"right",7} , {"up",3}, {"down",4}} },
            {12 , new Dictionary<string, int>{{"left",1} , {"right",4} , {"up",10}, {"down",8}} },
        };
        if(ExperimentManager.Instance != null)
        {
            ExperimentData experimentData = ExperimentManager.Instance.loadedExperimentData;  // Use the shared class

            if (experimentData != null)
            {
                // Retrieve the config data
                //gridSize = (landmarkData.grid_size, landmarkData.grid_size);
                
                // Set grid size (if you have a grid-based system)
                // Create landmarks based on the config data
                Debug.Log(experimentData.board_data);
                CreateLandmarks(experimentData.board_data);
            }
            else
            {
                Debug.LogError("Failed to load config data from ExperimentManager.");
            }
        }
    }

    void CreateLandmarks(BoardData[] boardData)
    {
        Debug.Log("setting up the Scene");
        // Get the reference to the GridBoard (assuming there's only one GridBoard object in the scene)
        GridBoard gridBoard = GameObject.FindGameObjectsWithTag("Grids")[0].GetComponent<GridBoard>();


        foreach (var data in boardData)
        {
            GameObject obj = null;
            int gridX = (int)data.goal_state.x_coordinate;
            int gridZ = (int)data.goal_state.z_coordinate;
            // Determine the object type (cube, ball, capsule, etc.)
            switch (data.body.ToLower())
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
                case "diamond":
                    if(Pyramid != null)
                        obj = GameObject.Instantiate(Diamond);
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
                    Debug.LogError($"Unknown object type: {data.body}");
                    continue;
            }

            // Use the 'coordinate' array to set the object's position
            Debug.Log($"SomeMethod called with x={gridX}, z={gridZ}");
            obj.transform.position = new Vector3(gridX, 0, gridZ);   
            //TODO
            //GPT suggests obj.transform.position = gridBoard.getGridWorldPos(gridX, gridZ);


            obj.transform.rotation = Quaternion.identity;
            obj.tag = "Commandable";  // Example tag for interactable objects
            obj.AddComponent<TargetBehaviour>();  // Assuming you have this script
            obj.GetComponent<TargetBehaviour>().SetInfo(data.body.ToLower(),data.color, data.geom_nr);
            // Set object color based on the 'color' property in the data data
            Material mat = new Material(Shader.Find("Standard"));
            Color objectColor;
            if (ColorUtility.TryParseHtmlString(data.color, out objectColor))
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
                Debug.LogWarning($"Invalid color: {data.color}, setting to magenta.");
                mat.color = Color.magenta;  // Default color if the color string is invalid
                obj.GetComponent<Renderer>().material = mat;
            }

            // Assuming TargetBehaviour is a script that manages positioning on a grid
            if(!ExperimentManager.Instance.loadedExperimentData.use_rendering)
            {
                obj.GetComponent<MeshRenderer>().enabled = false;
            }
            TargetBehaviour targetBehaviour = obj.GetComponent<TargetBehaviour>();
            // Assign the same GridBoard reference that LevelManager uses
            targetBehaviour.SetOrientationMap(orientationMap);
            targetBehaviour.SetFlipTransitionMap(flipTransitionMap);

            targetBehaviour.setPositionOnGrid((int)data.goal_state.x_coordinate, (int)data.goal_state.z_coordinate);
            targetBehaviour.setGoalPos((int)data.goal_state.x_coordinate, (int)data.goal_state.z_coordinate);
            targetBehaviour.setStartPos((int)data.start_state.x_coordinate, (int)data.start_state.z_coordinate);

            targetBehaviour.setGoalOrientaion((int)data.goal_state.orientation);
            targetBehaviour.setStartOrientaion((int)data.start_state.orientation);
            targetBehaviour.setOrientation((int)data.goal_state.orientation);

            targetBehaviour.setGoalOnBoard((int)data.goal_state.on_board);
            targetBehaviour.setStartOnBoard((int)data.start_state.on_board);
            targetBehaviour.setOnBoard((int)data.goal_state.on_board);
            if(data.body.ToLower() == "tile")
            {
                int objectID = Animator.StringToHash(data.body.ToLower() + " " + data.geom_nr.ToLower());
                Debugger.Instance.objectList.Add(objectID, data.body.ToLower() + " " + data.geom_nr.ToLower());
                targetBehaviour.SetID(objectID);
            }
            else
            {
                int objectID = Animator.StringToHash(data.color.ToLower() + " " + data.body.ToLower());
                Debugger.Instance.objectList.Add(objectID, data.color.ToLower() + " " + data.body.ToLower());
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
