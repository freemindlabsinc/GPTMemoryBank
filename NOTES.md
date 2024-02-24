### Questions

1) How do I separate the Gradio app from the API?
    - They should be separate and deployed separately.
    - The Gradio app should be a client to the API (REST).

2) What is the complete API that the Gradio client and the GPT require?
    - Are they the same? (*probably not*)
        - The API surface needed in the Gradio client is wider than the GPT Actions need. - Our UI does everything: the GPT does only some of the things the UI does.
            - In GTP I mostly need to read from the memory bank
            - Potentially I could tell it to download from a link and add to the memory bank, but our UI gives more flexibility.

        - We should explore the needs of the client first, and then see what parts can be shared as a GPT action. It should naturally fall out of the design of the client.

    
        
## Use Cases

### Memory Stream Manager Tab

The stream manager tab allows the users to connect to their sources of interest (i.e. the memory streams). Each of the connections is a separate memory stream.

Examples include:
    - Local Folder(s)        
    - Google drive shared folder(s)
    - Web link(s)
    - Database(s)

Workflow:
    1) User selects a source type
    2) User provides the necessary information to connect to the source
    3) User provides a name for the stream
    4) User provides a description for the stream
    5) User provides a list of tags for the stream
    

#### Features/Limitations

- Non paying users can only have X streams and they are limited to Y items per stream.