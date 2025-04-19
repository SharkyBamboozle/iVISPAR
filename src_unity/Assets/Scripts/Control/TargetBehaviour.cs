using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.Threading;
using UnityEngine.Events;
using Unity.VisualScripting;
using System.Net.Http.Headers;
using System;
using System.Runtime.CompilerServices;

public class TargetBehaviour : MonoBehaviour
{

    public GridBoard gridBoard; 
    //public CaptureCamera camcorder; not used
    //public List<Material> mats; not used
    public bool isInitialized = false;
    // Start is called before the first frame update
    private Vector3 boundPosition;
    private int x = -1;
    private int z = -1;

    private int goal_x = -1;

    private int goal_z = -1;

    private int start_x = -1;

    private int start_z = -1;

    private int startOrientation = 0;
    private int goalOrientation = 0;
    private int currentOriantation = 0;
    private int objectID;
    public void SetID(int ID)
    {
        objectID = ID;
    }
    private string objectType;
    private string objectColor;

    private string geomNumber;
    public Dictionary<int,Vector3> orientationMap;
    public Dictionary<int,Dictionary<string,int>> flipTransitionMap;

    private int onBoard = 0;
    private int goalOnBoard = 0;
    private int startOnBoard = 0;
    void Start()
    {
        
        if(gridBoard == null)
        {
            gridBoard = GameObject.FindGameObjectsWithTag("Grids")[0].GetComponent<GridBoard>();
            //Debug.LogError("GridBoard Not Selected");
        }
        //boundPosition = gridBoard.getBoundPos();
        if(x == -1 && z == -1)
            Debug.LogError("Position of target " + objectID.ToString() + " is not correctly set");
        transform.position = gridBoard.getGridWorldPos(x,z) + (Vector3.one *  0.5f);
        if(objectType == "tile")
        {
             Vector3 offset = new Vector3(0f,0.25f,0f);
            transform.position -= offset;
            transform.GetComponent<TileLabel>().CreateLabel();
        }
           
        EventHandler.Instance.RegisterEvent("move",MoveObject);
        EventHandler.Instance.RegisterEvent("rotate",RotateObject);
        EventHandler.Instance.RegisterEvent("flip",FlipObject);
        EventHandler.Instance.RegisterEvent("setpos",SetPositionOnGrid);
        EventHandler.Instance.RegisterEvent("addremove",AddRemoveObject);
        EventHandler.Instance.RegisterEvent("init_target",InitTargets);


        // orientationMap = new Dictionary<int, Vector3>(){
        //     {1 , new Vector3(0f,0f,0f)},
        //     {2 , new Vector3(0f,90f,0f)},
        //     {3 , new Vector3(0f,180f,0f)},
        //     {4 , new Vector3(0f,270f,0f)},
        //     {5 , new Vector3(270f,180f,180f)},
        //     {6 , new Vector3(270f,180f,270f)},
        //     {7 , new Vector3(270f,180f,0f)},
        //     {8 , new Vector3(270f,180f,90f)},
        //     {9 , new Vector3(0,90f,270f)},
        //     {10 , new Vector3(0,180f,270f)},
        //     {11 , new Vector3(0,270f,270f)},
        //     {12 , new Vector3(0,0f,270f)}
        // };
        

        // flipTransitionMap = new Dictionary<int, Dictionary<string, int>>{
        //     {1 , new Dictionary<string, int>{{"left",8} , {"right",8} , {"up",9}, {"down",5}} },
        //     {2 , new Dictionary<string, int>{{"left",6} , {"right",10} , {"up",5}, {"down",9}} },
        //     {3 , new Dictionary<string, int>{{"left",10} , {"right",6} , {"up",7}, {"down",11}} },
        //     {4 , new Dictionary<string, int>{{"left",12} , {"right",8} , {"up",11}, {"down",7}} },
        //     {6 , new Dictionary<string, int>{{"left",3} , {"right",2} , {"up",8}, {"down",10}} },
        //     {7 , new Dictionary<string, int>{{"left",11} , {"right",5} , {"up",4}, {"down",3}} },
        //     {8 , new Dictionary<string, int>{{"left",4} , {"right",1} , {"up",12}, {"down",6}} },
        //     {9 , new Dictionary<string, int>{{"left",5} , {"right",11} , {"up",2}, {"down",1}} },
        //     {10 , new Dictionary<string, int>{{"left",2} , {"right",3} , {"up",6}, {"down",12}} },
        //     {11 , new Dictionary<string, int>{{"left",9} , {"right",7} , {"up",3}, {"down",4}} },
        //     {12 , new Dictionary<string, int>{{"left",1} , {"right",4} , {"up",10}, {"down",8}} },
        // };
        
    }
    public void SetOrientationMap(Dictionary<int,Vector3> orientationMap)
    {
        this.orientationMap = orientationMap;
    }

    public void SetFlipTransitionMap(Dictionary<int, Dictionary<string, int>> flipTransitionMap)
    {
        this.flipTransitionMap = flipTransitionMap;
    }
    public void setOrientation(int state)
    {
        transform.eulerAngles = orientationMap[state];
        currentOriantation = state;
    }
    public string getObjectStatus()
    {
        return string.Format("{0} {1} is at ({2},{3})",objectColor,objectType,x,z);
    }
    public string getObjectChessStatus()
    {
        return string.Format("{0} {1} {2}",gridBoard.GridCoordinatesToChess(x,z),objectColor,objectType);
    }
    public ObjectData GetObjectData()
    {
        ObjectData board_data = new ObjectData();
        board_data.body = objectType;
        board_data.color = objectColor;
        board_data.current_coordinate = new float[2];
        board_data.current_coordinate[0] = x;
        board_data.current_coordinate[1] = z;
        board_data.goal_coordinate = new float[2];
        board_data.goal_coordinate[0] = goal_x;
        board_data.goal_coordinate[1] = goal_z;
        board_data.current_orientation = currentOriantation;
        board_data.goal_orienation = goalOrientation;
        board_data.current_on_board = onBoard;
        board_data.goal_on_board = goalOnBoard;
        return board_data;
    }
    public void SetInfo(string type, string color, string geomNum)
    {
        objectType = type;
        objectColor = color;
        geomNumber = geomNum;
    }
    public string getGeomNumber()
    {
        return geomNumber;
    }
    // Update is called once per frame
    void Update()
    {
             
    }
    public void setPositionOnGrid(int x, int z)
    {
        this.x = x;
        this.z = z;
        Debug.LogWarning("setPositionOnGrid x:" +x +", z: " +z);

    }

    public void setGoalPos(int x, int z)
    {
        this.goal_x = x;
        this.goal_z = z;
        Debug.LogWarning("setGoalPos x:" +x +", z: " +z);
    }
    public void setGoalOnBoard(int state)
    {
        this.goalOnBoard = state;
        Debug.LogWarning("goalOnBoard : " + state );
    }
    public void setStartOnBoard(int state)
    {
        this.startOnBoard = state;
        Debug.LogWarning("startOnBoard : " + state );
    }
    public void setOnBoard(int state)
    {
        this.onBoard = state;
        if(state == 1)
        {
            AddObject();
        }
        else if(state == 0)
        {
            RemoveObject();
        }
        
    }
    public bool evaluateGoal()
    {
        Debug.LogFormat("for {0} object foal coordinates are ({1},{2}) , current cordinate is ({3},{4})",Debugger.Instance.objectList[objectID], this.goal_x, this.goal_z, this.x, this.z);
        if((this.goal_x == this.x) && (this.goal_z == this.z) && (this.goalOrientation == this.currentOriantation) && (this.onBoard == this.goalOnBoard))
            return true;
        else
            return false;
    }
    public void setStartPos(int x, int z)
    {
        this.start_x = x;
        this.start_z = z;
        Debug.LogWarning("setStartPos x:" +x +", z: " +z);
    }
    public void setStartOrientaion(int state)
    {
        this.startOrientation = state;
        Debug.LogWarning("setStartOrientation to:" +state);
    }
    public void setGoalOrientaion(int state)
    {
        this.goalOrientation = state;
        Debug.LogWarning("setGoalOrientation to:" +state);
    }
    public void FlipObject(int ID ,string direction)
    {
        if(isInitialized)
        {
            if(objectID == ID)
            {
                Flip(direction);     
            }
        }
        else
        {
            Debugger.Instance.SetValidity("you can not flip before start action");
        }        
    }
    public void AddRemoveObject(int ID, string actionType )
    {
        if(isInitialized)
        {
           
           if(objectID == ID)
            {
                if(actionType == "delete")
                {
                    RemoveObject();
                }
                else if (actionType == "add")
                {
                    AddObject();
                }
                       
            }
             
        }
        else
        {
            Debugger.Instance.SetValidity("you can not add or remove object before start action");
        }    
    }
    public void RemoveObject()
    {
        if(transform.GetComponent<MeshRenderer>().enabled == true)
        {
            transform.GetComponent<MeshRenderer>().enabled = false;
            transform.GetChild(0).GetComponent<MeshRenderer>().enabled = false;
            gridBoard.setOccupancy(x,z,false);
            gridBoard.SetObjectUID(x,z,0);
            Debugger.Instance.SetValidity("action was valid");
            if(ExperimentManager.Instance.loadedExperimentData.auto_done_check || ExperimentManager.Instance.humanExperiment)
                EventHandler.Instance.InvokeCommand("AutoDoneCheck"); 
        }
        else
        {
            Debugger.Instance.SetValidity("invalid action since object does not exist on the board");
        }  
    }
    public void AddObject()
    {
        if(transform.GetComponent<MeshRenderer>().enabled == false)
        {
            if(!gridBoard.GetOccupany(x,z))
            {
                transform.GetComponent<MeshRenderer>().enabled = true;
                transform.GetChild(0).GetComponent<MeshRenderer>().enabled = true;
                gridBoard.setOccupancy(x,z,true);
                gridBoard.SetObjectUID(x,z,objectID);
                if(ExperimentManager.Instance.loadedExperimentData.auto_done_check || ExperimentManager.Instance.humanExperiment)
                    EventHandler.Instance.InvokeCommand("AutoDoneCheck");
            }
            else
                Debugger.Instance.SetValidity("invalid action since object position is occupied");
        }
        else
        {
            Debugger.Instance.SetValidity("invalid action since object already exist on the board");
        }         
    }
    public void Flip(string direction)
    {
        int state = currentOriantation;
        int nextSate = flipTransitionMap[currentOriantation][direction];
        setOrientation(nextSate);
        currentOriantation = nextSate;
        Debugger.Instance.SetValidity("was legal action");
        if(ExperimentManager.Instance.loadedExperimentData.auto_done_check || ExperimentManager.Instance.humanExperiment)
            EventHandler.Instance.InvokeCommand("AutoDoneCheck"); 
    }
    /*public void Rotate( int xOffset,int zOffset, List<(int,int)> offsetList)
    {
        if( 0 <= (z + zOffset) &&  (z + zOffset) < gridBoard.height && 0 <= (x + xOffset) &&  (x + xOffset) < gridBoard.width)
        {
            List<int> ObjectIDs = new List<int>();
            gridBoard.setOccupancy(offsetList[0].Item1,offsetList[0].Item2,false);
            ObjectIDs.Add(gridBoard.GetObjectUID(offsetList[0].Item1,offsetList[0].Item2));
            gridBoard.setOccupancy(offsetList[1].Item1,offsetList[1].Item2,false);
            ObjectIDs.Add(gridBoard.GetObjectUID(offsetList[1].Item1,offsetList[1].Item2));
            gridBoard.setOccupancy(offsetList[2].Item1,offsetList[2].Item2,false);
            ObjectIDs.Add(gridBoard.GetObjectUID(offsetList[2].Item1,offsetList[2].Item2));
            gridBoard.setOccupancy(offsetList[3].Item1,offsetList[3].Item2,false);
            ObjectIDs.Add(gridBoard.GetObjectUID(offsetList[3].Item1,offsetList[3].Item2));
            
            
            
            if(id != 0)
            {
                EventHandler.Instance.InvokeCommand("move",id,directionSet[0]);
                gridBoard.setOccupancy(offsetList[0].Item1,offsetList[0].Item2,true);
            }
            id = gridBoard.GetObjectUID(offsetList[1].Item1,offsetList[1].Item2);
            if(id != 0)
            {   
                EventHandler.Instance.InvokeCommand("move",id,directionSet[1]);
                gridBoard.setOccupancy(offsetList[1].Item1,offsetList[1].Item2,true);
            }
            id = gridBoard.GetObjectUID(offsetList[2].Item1,offsetList[2].Item2);
            if(id != 0)
            {
                EventHandler.Instance.InvokeCommand("move",id,directionSet[2]);
                gridBoard.setOccupancy(offsetList[2].Item1,offsetList[2].Item2,true);
            }
            id = gridBoard.GetObjectUID(offsetList[3].Item1,offsetList[3].Item2);
            if(id != 0)
            {
                EventHandler.Instance.InvokeCommand("move",id,directionSet[3]);
                gridBoard.setOccupancy(offsetList[3].Item1,offsetList[3].Item2,true);
            }
            
        }
        else
            Debugger.Instance.SetValidity("Destination out of bounds");
        if(ExperimentManager.Instance.loadedLandmarkData.auto_done_check || ExperimentManager.Instance.humanExperiment)
            EventHandler.Instance.InvokeCommand("AutoDoneCheck"); 
    }*/
    public void RotateObject(int ID, string direction)
    {
        if(isInitialized)
        {
            if(objectID == ID)
            {
                List<string> directionSet = new List<string>();
                List<(int,int)> offsetList = new List<(int, int)>();
                List<(int,int)> destinamtionList = new List<(int, int)>();
                int xOffset = 0;
                int zOffset = 0;
                if(direction == "top-left" || direction == "up-left")
                {
                    xOffset = -1;
                    zOffset = 1;
                    offsetList.Add((x,z));
                    offsetList.Add((x-1,z));
                    offsetList.Add((x-1,z+1));
                    offsetList.Add((x,z+1));
                }
                else if(direction == "top-right" || direction == "up-right")
                {
                    xOffset = 1;
                    zOffset = 1;
                    offsetList.Add((x,z));
                    offsetList.Add((x,z+1));
                    offsetList.Add((x+1,z+1));
                    offsetList.Add((x,z+1));
                }
                else if(direction == "bottom-left" || direction == "down-left")
                {
                    xOffset = -1;
                    zOffset = -1;
                    offsetList.Add((x,z));
                    offsetList.Add((x,z-1));
                    offsetList.Add((x-1,z-1));
                    offsetList.Add((x-1,0));
                }
                else if(direction == "bottom-right" || direction == "down-right")
                {
                    xOffset = 1;
                    zOffset = -1;
                    offsetList.Add((x,z));
                    offsetList.Add((x+1,z));
                    offsetList.Add((x+1,z-1));
                    offsetList.Add((x,z-1));
                }
                //Rotate(xOffset,zOffset,offsetList);
            }
        }
        else
            Debugger.Instance.SetValidity("you can not move before start action");
        
    }
    public void SetPositionOnGrid(int ID, string position)
    {
        string [] posXZ = position.Split(",");
        int posX = int.Parse(posXZ[0]);
        int posZ = int.Parse(posXZ[0]);
        transform.position = gridBoard.getGridWorldPos(posX, posZ) + (transform.localScale /2);
        gridBoard.setOccupancy(posX,posZ,true);
        gridBoard.SetObjectUID(posX,posZ,ID);
    }
    public void MoveObject(int ID ,string direction)
    {
        if(isInitialized)
        {
            if(objectID == ID)
            {
                if(direction == "up")
                    MoveForward(1);
                if(direction == "down")
                    MoveForward(-1); 
                if(direction == "right")
                    MoveRight(1);   
                if(direction == "left")
                    MoveRight(-1);        
            }
        }
        else
        {
            Debugger.Instance.SetValidity("you can not move before start action");
        }        
    }


    public void InitTargets()
    {
        Debug.Log("Randomizing object");
        //Debug.LogWarning("Move command invoked with direction " + direction);
            // Update the x and z coordinates before updating the position
        x = start_x;
        z = start_z;
        transform.position = gridBoard.getGridWorldPos(x, z) + (transform.localScale /2);
        gridBoard.setOccupancy(x,z,true);
        gridBoard.SetObjectUID(x,z,objectID);
        setOrientation(startOrientation);
        setOnBoard(startOnBoard);
        isInitialized = true;
        Debug.Log(gridBoard.GridOccupanyLog());
        Debugger.Instance.SetValidity("set objects position to initial positions");
    }


    public void MoveForward(int units)
    {
        if( 0 <= (z + units) &&  (z + units) < gridBoard.height && !gridBoard.GetOccupany(x,z+units))
        {
            gridBoard.setOccupancy(x,z,false);
            gridBoard.SetObjectUID(x,z,0);
            z += units;
            transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
            gridBoard.setOccupancy(x,z,true);
            gridBoard.SetObjectUID(x,z,objectID);
            Debugger.Instance.SetValidity("was legal move");  
        }
        else if(gridBoard.GetOccupany(x,z+units)) 
            Debugger.Instance.SetValidity("Destination occupied");
        else
            Debugger.Instance.SetValidity("Destination out of bounds");
        if(ExperimentManager.Instance.loadedExperimentData.auto_done_check || ExperimentManager.Instance.humanExperiment)
            EventHandler.Instance.InvokeCommand("AutoDoneCheck"); 
    }
    public void MoveRight(int units)
    {
        if( 0 <= (x + units) &&  (x + units) < gridBoard.width && !gridBoard.GetOccupany(x+units,z))
        {
            gridBoard.setOccupancy(x,z,false);
            gridBoard.SetObjectUID(x,z,0);
            x += units;
            transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
            gridBoard.setOccupancy(x,z,true);
            gridBoard.SetObjectUID(x,z,objectID);
            Debugger.Instance.SetValidity("was legal move");          
        }
        else if(gridBoard.GetOccupany(x+units,z)) 
            Debugger.Instance.SetValidity("Destination occupied");
        else
            Debugger.Instance.SetValidity("Destination out of bounds");
        if(ExperimentManager.Instance.loadedExperimentData.auto_done_check || ExperimentManager.Instance.humanExperiment)
            EventHandler.Instance.InvokeCommand("AutoDoneCheck"); 
    }

    public Vector2 goalCoordinate
    {
        get
        {
            return new Vector2(goal_x, goal_z);  // Assuming 2D check on x (for x-axis) and y (for z-axis)
        }
    }
    private void OnDestroy() 
    {
        EventHandler.Instance.UnregisterEvent("move",MoveObject);
        EventHandler.Instance.UnregisterEvent("flip",FlipObject);
        EventHandler.Instance.UnregisterEvent("rotate",RotateObject);
        EventHandler.Instance.UnregisterEvent("addremove",AddRemoveObject);
        EventHandler.Instance.UnregisterEvent("init_target",InitTargets);
        EventHandler.Instance.UnregisterEvent("setpos",SetPositionOnGrid);
    }

}
