using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CheckBoardVIsualizer : MonoBehaviour
{
    private GridBoard grid; 
    private MeshFilter meshFilter;
    private Mesh mesh;

    private int maxUVValue = 100;

    [Range(0,100)]
    public int targetGradiant = 80;
    void Start()
    {
        grid = GetComponent<GridBoard>();
        meshFilter = GetComponent<MeshFilter>();
        mesh = new Mesh();
        meshFilter.mesh = mesh;
        Vector3[] vertices;
        Vector2[] uv;
        int[] triangles;

        MeshUtils.CreateEmptyMeshArrays(grid.width * grid.height, out vertices,out uv ,out triangles);
        for(int x = 0 ; x < grid.width ; x++)
            for(int z = 0 ; z < grid.height; z++)
            {
                int index = x * grid.height + z;
                
                Vector3 baseSize = new Vector3(1, 0 ,1) * grid.cellSize;
                int gradiantValue = targetGradiant * (index%2);
                float gradiantValueNormalized = Mathf.Clamp01((float)gradiantValue / maxUVValue);
                Vector2 gradiantCellUV = new Vector2(gradiantValueNormalized, 1f);
                
                MeshUtils.AddToMeshArrays(vertices, uv, triangles, index, grid.getGridWorldPos(x, z) - transform.position + (baseSize * 0.5f) , 0f, baseSize , gradiantCellUV, gradiantCellUV);
            }
        mesh.vertices = vertices;
        mesh.uv = uv;
        mesh.triangles = triangles;
    }

    
}
