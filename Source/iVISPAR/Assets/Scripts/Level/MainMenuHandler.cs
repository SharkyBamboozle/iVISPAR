using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using TMPro;
public class MainMenuHandler : MonoBehaviour
{
    // Start is called before the first frame update
    public GameObject inputField;
    public TextMeshPro message;
    void Awake()
    {
        if(ExperimentManager.Instance.isConnected)
        {
            inputField.SetActive(false);
            message.text = "you are connected. set new setup";
            
        }
        else
        {
            inputField.SetActive(true);
            message.text = "you id is:";
        }

    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
