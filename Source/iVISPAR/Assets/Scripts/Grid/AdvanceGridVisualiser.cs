using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;

public enum LabelType
{
    none,
    edge,
    cell,
    both  
}
public class AdvanceGridVisualiser : MonoBehaviour
{
    
    private GridBoard grid; 
    private MeshFilter meshFilter;
    private Mesh mesh;
 

    [Range(0f,1f)]
    public float chunkSize= 0.2f;

    public Color darkColor = Color.grey;
    public Color lightColor = Color.yellow;

    public int fontSize = 7;
    public int cellFontSize = 4;
    public float labelSize = 2f;
    public Color labelLightColor = Color.white;
    public Color labelDarkColor = Color.black;

    public LabelType labelType = LabelType.none;
    public Vector3 threeLetterLableOffset = new Vector3(1.0f,0.1f,-0.25f);
    public Vector3 twoLetterLableOffset = new Vector3(1.0f,0.1f,-0.25f);

    void Awake()
    {
        if(!ExperimentManager.Instance.loadedLandmarkData.use_rendering)
        {
            this.enabled = false;
        }    
    }


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
        int counter = 0;
        MeshUtils.CreateEmptyMeshArrays(grid.width * grid.height, out vertices,out vertexColors,out uv ,out triangles);
        if(ExperimentManager.Instance != null)
            SetLabelType(ExperimentManager.Instance.loadedLandmarkData.grid_label);
        for(int x = 0 ; x < grid.width ; x++)
            for(int z = 0 ; z < grid.height; z++)
            {
                if(x == 0 && (labelType == LabelType.edge || labelType == LabelType.both))
                {
                    string label = (z+1).ToString();
                    GameObject myTextObject = new GameObject(label);
                    myTextObject.AddComponent<TextMeshPro>();
                    TextMeshPro textMeshComponent = myTextObject.GetComponent<TextMeshPro>();
                    textMeshComponent.rectTransform.Rotate(new Vector3(90,0,0));
                    textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal,labelSize);
                    textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical,labelSize);
                    textMeshComponent.rectTransform.position = grid.getGridWorldPos(x, z);
                    textMeshComponent.rectTransform.SetParent(this.transform);
                    textMeshComponent.text = label;
                    textMeshComponent.fontSize = fontSize;
                    
                }
                if(z == 0 && (labelType == LabelType.edge || labelType == LabelType.both))
                {
                    string lable = ConvertNumberToLetter(x+1);
                    GameObject myTextObject = new GameObject(lable);
                    myTextObject.transform.rotation.eulerAngles.Set(90,0,0);
                    myTextObject.AddComponent<TextMeshPro>();
                    TextMeshPro textMeshComponent = myTextObject.GetComponent<TextMeshPro>();
                    textMeshComponent.rectTransform.Rotate(new Vector3(90,0,0));
                    textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal,labelSize);
                    textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical,labelSize);     
                    textMeshComponent.rectTransform.position = grid.getGridWorldPos(x, z) + new Vector3(1.25f,0,-1.25f);
                    textMeshComponent.rectTransform.SetParent(this.transform);
                    textMeshComponent.text = lable;
                    textMeshComponent.fontSize = fontSize;
                    
                }
                if(labelType == LabelType.cell || labelType == LabelType.both)
                {
                    string lable = ConvertNumberToLetter(x+1) + (z+1).ToString();
                    GameObject myTextObject = new GameObject(lable);
                    myTextObject.transform.rotation.eulerAngles.Set(90,0,0);
                    myTextObject.AddComponent<TextMeshPro>();
                    TextMeshPro textMeshComponent = myTextObject.GetComponent<TextMeshPro>();
                    textMeshComponent.rectTransform.Rotate(new Vector3(90,0,0));
                    textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Horizontal,labelSize);
                    textMeshComponent.rectTransform.SetSizeWithCurrentAnchors(RectTransform.Axis.Vertical,labelSize);
                    if(lable.Length == 3)     
                        textMeshComponent.rectTransform.position = grid.getGridWorldPos(x, z) + threeLetterLableOffset;
                    else
                        textMeshComponent.rectTransform.position = grid.getGridWorldPos(x, z) + twoLetterLableOffset;
                    textMeshComponent.rectTransform.SetParent(this.transform);
                    textMeshComponent.text = lable;
                    textMeshComponent.fontSize = cellFontSize;
                    textMeshComponent.fontStyle = FontStyles.Bold;

                    if (colorIndex%2 == 0)
                        textMeshComponent.color = labelLightColor;
                    else
                        textMeshComponent.color = labelDarkColor;
                }
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
                counter++;
                if(counter  % grid.width ==  0 && grid.width % 2 == 0)
                {
                    counter = 0;
                    colorIndex++;
                }               
           }
        
        mesh.vertices = vertices;
        mesh.uv = uv;
        mesh.triangles = triangles;
        mesh.colors32 = vertexColors;
        
        
    }

    string ConvertNumberToLetter(int number)
    {
        if (number < 1 || number > 26)
        {
            return "Invalid"; // Return "Invalid" for out-of-range numbers
        }

        char letter = (char)('A' + number - 1); // Calculate the corresponding letter
        return letter.ToString();
    }
    private void SetLabelType(string type)
    {
        switch (type)
        {
            case "none":
                labelType = LabelType.none;
                break;
            case "edge":
                labelType = LabelType.edge;
                break;
            case "cell":
                labelType = LabelType.cell;
                break;
            case "both":
                labelType = LabelType.both;
                break;
        }
    }
}