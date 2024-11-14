using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AdvanceGridVisualiser : MonoBehaviour
{
    
    private GridBoard grid; 
    private MeshFilter meshFilter;
    private Mesh mesh;
 

    [Range(0f,1f)]
    public float chunkSize= 0.2f;

    public Color darkColor = Color.grey;
    public Color lightColor = Color.yellow;

    void Start()
    {
        grid = GetComponent<GridBoard>();
        meshFilter = GetComponent<MeshFilter>();
        mesh = new Mesh();
        meshFilter.mesh = mesh;
        Vector3[] vertices;
        Color32[] vertexColors;
        Vector2[] uv;
        int[] triangles;
        int colorIndex = 0;
        MeshUtils.CreateEmptyMeshArrays(grid.width * grid.height, out vertices,out vertexColors,out uv ,out triangles);
        for(int x = 0 ; x < grid.width ; x++)
            for(int z = 0 ; z < grid.height; z++)
            {
                int index = x * grid.height + z;
                
                Vector3 baseSize = new Vector3(1, 0 ,1) * grid.cellSize;
                Color vertexColor = Color.black;
                if (colorIndex%2 == 0)
                    vertexColor = darkColor;
                else
                    vertexColor = lightColor;
                float startPos = Random.Range(0f, 1f - chunkSize);
                Vector2 u0 = new Vector2(startPos,startPos);
                Vector2 u1 = new Vector2(startPos + chunkSize,startPos + chunkSize);
                
                MeshUtils.AddToMeshArrays(vertices,vertexColors, uv, triangles, index, grid.getGridWorldPos(x, z) - transform.position + (baseSize * 0.5f) , 0f, baseSize , u0, u1,vertexColor);
                colorIndex++;
                if(colorIndex % grid.width == 0 && grid.width % 2 == 0)
                    colorIndex++;
           }
        mesh.vertices = vertices;
        mesh.uv = uv;
        mesh.triangles = triangles;
        mesh.colors32 = vertexColors;
        
        
    }
}
