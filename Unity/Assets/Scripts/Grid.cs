using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Grid {
    private int width = 1;
    private int height = 1;
    private Vector3 originPos;
    private float cellSize = 1.0f;
    private bool[,] isOccupied;


    private Color lineColor;
    private float lineWidth; 

    public Grid(int width, int height, float cellSize, Vector3 originPos, Color lineColor, float lineWidth)
    {
        this.width = width;
        this.height = height;
        this.cellSize = cellSize;
        this.originPos = originPos;
        this.lineColor = lineColor;
        this.lineWidth = lineWidth;
        isOccupied = new bool[width,height];
        Debug.Log("Created a grid with the width of " +  width + " and height of " + height );
        
        for(int x = 0 ; x < width; x++) 
            for(int z = 0 ; z < height; z++)
            {
                isOccupied[x,z] = false;
                Debug.DrawLine(GetWorldPosition(x,z), GetWorldPosition(x , z+1),lineColor,lineWidth);
                Debug.DrawLine(GetWorldPosition(x,z), GetWorldPosition(x+1 , z),lineColor,lineWidth);
            }
        Debug.DrawLine(GetWorldPosition(0,height), GetWorldPosition(width , height),lineColor,lineWidth);
        Debug.DrawLine(GetWorldPosition(width,0), GetWorldPosition(width , height),lineColor,lineWidth);
    }
    
    public Vector3 GetWorldPosition(int x, int z)
    {
        return new Vector3(x,0,z) * cellSize + originPos;
    }

    public void GetGridPosition(Vector3 worldPosition, out int x, out int z)
    {
        x = Mathf.FloorToInt((worldPosition - originPos).x / cellSize);
        z = Mathf.FloorToInt((worldPosition - originPos).z / cellSize);
    }

    public bool GetOccupany(int x, int z)
    {
        return isOccupied[x,z];
    }
    
    public void setOccupancy(int x, int z, bool state)
    {
        isOccupied[x,z] = state;
    }
}
