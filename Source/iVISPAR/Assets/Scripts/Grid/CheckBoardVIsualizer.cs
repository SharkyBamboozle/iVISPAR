using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class CheckBoardVIsualizer : MonoBehaviour
{
    private GridBoard grid; 
    private MeshFilter meshFilter;
    private Mesh mesh;

    private int maxUVValue = 100;

    public Font lableFont;
	public Material lableFontMaterial;

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
        {
            for(int z = 0 ; z < grid.height; z++)
            {
                if(x == 9)
                {
                    // create vertival lables
                    GameObject myTextObject = new GameObject("Lable");
                    myTextObject.AddComponent<TextMesh>();
                    myTextObject.AddComponent<MeshRenderer>();
                    // Get components
                    TextMesh textMeshComponent = myTextObject.GetComponent(typeof(TextMesh)) as TextMesh;
                    MeshRenderer meshRendererComponent = myTextObject.GetComponent(typeof(MeshRenderer)) as MeshRenderer;
            
                    // Set font of TextMesh component (it works according to the inspector)
                    textMeshComponent.font = lableFont;
                    textMeshComponent.text = "Test";
                    meshRendererComponent.materials[0].color = Color.black;
                    // Create an array of materials for the MeshRenderer component (it works according to the inspector)
                    //meshRendererComponent.materials = new Material[1];
                }
                int index = x * grid.height + z;
                
                Vector3 baseSize = new Vector3(1, 0 ,1) * grid.cellSize;
                int gradiantValue = targetGradiant * (index%2);
                float gradiantValueNormalized = Mathf.Clamp01((float)gradiantValue / maxUVValue);
                Vector2 gradiantCellUV = new Vector2(gradiantValueNormalized, 1f);
                
                MeshUtils.AddToMeshArrays(vertices, uv, triangles, index, grid.getGridWorldPos(x, z) - transform.position + (baseSize * 0.5f) , 0f, baseSize , gradiantCellUV, gradiantCellUV);
            }
        }
        mesh.vertices = vertices;
        mesh.uv = uv;
        mesh.triangles = triangles;
    }

    
}
