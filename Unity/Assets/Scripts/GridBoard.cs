using System;
using System.Collections;
using System.Collections.Generic;
using System.Data.Common;
using UnityEngine;


public class GridBoard : MonoBehaviour
/*This class defines the grid board based on the Grid object it holds */
{
    public Grid grid;
    public int width; //length of the grid board in one dimension (doesn't effect the grid yet because meta file is read first)
    public int height; //length of the grid board in another dimension (doesn't effect the grid yet because meta file is read first)

    [Range(0.0f, 100.0f)]
    public float cellSize = 1.0f; //scale size of each cell
    [Header("Debug parameters")]
    public Color lineColor = Color.red; //color of the line, only visible in the editor
    public float lineWidth = 500f;

    public CameraAdjustment camAdjustmet;
    public void setGridSize(int width, int height)
    {
        this.width = width;
        this.height = height;
    }
    void Awake()
    /*Gets called when Environment is set up and initializes the grid*/
    {
        
        if(ExperimentManager.Instance != null)
        {
            ExperimentManager experimentManager = ExperimentManager.Instance;
            LandmarkData landmarkData = experimentManager.GetLandmarkData();  // Use the shared class

            if (landmarkData != null)
            {
                
                this.width = this.height = landmarkData.grid_size;
            }
            else
            {
                Debug.LogError("Failed to load config data from ExperimentManager.");
            }
        }
        grid = new Grid(width,height,cellSize,transform.position,lineColor,lineWidth);

        Vector3 centerPos = grid.GetWorldPosition((int)(width/2) ,  (int)(height/2));
        camAdjustmet.SetPostition(centerPos.x,centerPos.z - (height));
        
    }
  
    public void GetRandomPostion(out int x, out int z)
    /*Returns a random legal position on the grid, e.g. to make a new random configuration*/
    {
        x = Mathf.FloorToInt(UnityEngine.Random.Range(0.0f, width));
        z = Mathf.FloorToInt(UnityEngine.Random.Range(0.0f, height));
    }

    public Vector3 getGridWorldPos(int x, int z)
    /*Transforms the coordinates into grid positions? */
    {
        return grid.GetWorldPosition(x,z);
    }

    public Vector3 getBoundPos()
    /*Returns size of the grid?*/
    {
        return grid.GetWorldPosition(width,height);
    }

    public bool GetOccupany(int x, int z)
    /*Return weather or not the location is occupied by an object, e.g. for collision detection*/
    {
        return grid.GetOccupany(x,z);
    }

    public void setOccupancy(int x, int z, bool state)
    /*Set a position to be occupied, e.g. if an object was moved or placed there*/
    {
        grid.setOccupancy(x,z,state);
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
