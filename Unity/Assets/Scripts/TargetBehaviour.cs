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
    public bool isPlayer = true;
    // Start is called before the first frame update
    private Vector3 boundPosition;
    private int x = -1;
    private int z = -1;

    private int goal_x = -1;

    private int goal_y = -1;

    private UnityEvent GenerateScreenshotEvent;

    private int objectID;
    public void SetID(int ID)
    {
        objectID = ID;
    }    
    void Start()
    {
        if (GenerateScreenshotEvent == null)
            GenerateScreenshotEvent = new UnityEvent();
        GenerateScreenshotEvent.AddListener(GameObject.FindWithTag("Server").GetComponent<Server>().GenerateScreenshot);
        if(gridBoard == null)
        {
            gridBoard = GameObject.FindGameObjectsWithTag("Grids")[0].GetComponent<GridBoard>();
            //Debug.LogError("GridBoard Not Selected");
        }
        boundPosition = gridBoard.getBoundPos();
        if(x == -1 && z == -1)
            gridBoard.GetRandomPostion(out x,out z);
        transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
        //transform.position = gridBoard.getGridWorldPos(x,z);
        if(!isPlayer)
            gridBoard.setOccupancy(x,z,true);
          
    }

    // Update is called once per frame
    void Update()
    {
        if(isPlayer)
        {
            if(Input.GetKeyDown(KeyCode.UpArrow))
                MoveForward(1);
            if(Input.GetKeyDown(KeyCode.DownArrow))
                MoveForward(-1); 
            if(Input.GetKeyDown(KeyCode.RightArrow))
                MoveRight(1);   
            if(Input.GetKeyDown(KeyCode.LeftArrow))
                MoveRight(-1);
        }        
    }
    public void setPositionOnGrid(int x, int z)
    {
        this.x = x;
        this.z = z;
    }

        public void setGoalPos(int x, int z)
    {
        this.goal_x = x;
        this.goal_y = z;
    }

    public void MovePlayer(int ID ,string direction)
    {
        //Debug.LogWarning("Move command invoked with direction " + direction);
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
            //GenerateScreenshotEvent.Invoke();
        } 
        
    }


    public void JumpPlayer()
    {
        Debug.Log("Randomizing object");
        //Debug.LogWarning("Move command invoked with direction " + direction);

        gridBoard.setOccupancy(x,z,false);
        gridBoard.GetRandomPostion(out x,out z);


        while (gridBoard.GetOccupany(x,z) == true)
        {
            gridBoard.GetRandomPostion(out x,out z);
        }

        transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
        gridBoard.setOccupancy(x,z,true);
    }


    public void MoveForward(int units)
    {
        if( 0 <= (z + units) &&  (z + units) < gridBoard.height && !gridBoard.GetOccupany(x,z+units)){
            gridBoard.setOccupancy(x,z,false);
            z += units;
            transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
            gridBoard.setOccupancy(x,z,true);
            //camcorder.CaptureFrame("Captures/" + Time.realtimeSinceStartup);
        }
    }
    public void MoveRight(int units)
    {
        if( 0 <= (x + units) &&  (x + units) < gridBoard.width && !gridBoard.GetOccupany(x+units,z)){
            gridBoard.setOccupancy(x,z,false);
            x += units;
            transform.position = gridBoard.getGridWorldPos(x,z) + (transform.localScale /2);
            gridBoard.setOccupancy(x,z,true);
            //camcorder.CaptureFrame("Captures/" + Time.realtimeSinceStartup);
        }
        //if(transform.position < boundPosition && transform.position > gridBoard.transform.position)
        //transform.position += (transform.right * units);
    }

    public Vector2 goalCoordinate
    {
        get
        {
            return new Vector2(goal_x, goal_y);  // Assuming 2D check on x (for x-axis) and y (for z-axis)
        }
    }

}
