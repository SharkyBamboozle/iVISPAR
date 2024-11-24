using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.Threading;
using UnityEngine.Events;
using Unity.VisualScripting;

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

        private int objectID;
    public void SetID(int ID)
    {
        objectID = ID;
    }
    private string objectType;
    private string objectColor;

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
        EventHandler.Instance.RegisterEvent("move",MovePlayer);
        EventHandler.Instance.RegisterEvent("init_target",InitTargets);
    }
    public string getObjectStatus()
    {
        return string.Format("{0} {1} is at ({2},{3})",objectColor,objectType,x,z);
    }
    public void SetInfo(string type, string color)
    {
        objectType = type;
        objectColor = color;
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
    public bool evaluateGoal()
    {
        Debug.LogFormat("for {0} object foal coordinates are ({1},{2}) , current cordinate is ({3},{4})",Debugger.Instance.objectList[objectID], this.goal_x, this.goal_z, this.x, this.z);
        if((this.goal_x == this.x) && (this.goal_z == this.z))
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

    public void MovePlayer(int ID ,string direction)
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
            Debugger.Instance.AppendLastLog(" - you can not move before start action");
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
        isInitialized = true;
        Debug.Log(gridBoard.GridOccupanyLog());
        Debugger.Instance.AppendLastLog(" - set objects position to initial positions"); 
    }


    public void MoveForward(int units)
    {
        if( 0 <= (z + units) &&  (z + units) < gridBoard.height && !gridBoard.GetOccupany(x,z+units))
        {
            gridBoard.setOccupancy(x,z,false);
            z += units;
            transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
            gridBoard.setOccupancy(x,z,true);
            Debugger.Instance.AppendLastLog(" - is legal move");  
        }
        else
            Debugger.Instance.AppendLastLog(" - is not legal move");
    }
    public void MoveRight(int units)
    {
        if( 0 <= (x + units) &&  (x + units) < gridBoard.width && !gridBoard.GetOccupany(x+units,z))
        {
            gridBoard.setOccupancy(x,z,false);
            x += units;
            transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
            gridBoard.setOccupancy(x,z,true);
            Debugger.Instance.AppendLastLog(" - is legal move");         
        }
        else
            Debugger.Instance.AppendLastLog(" - is not legal move"); 
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
        EventHandler.Instance.UnregisterEvent("move",MovePlayer);
        EventHandler.Instance.UnregisterEvent("init_target",InitTargets);
    }

}
