# PicFusion

**Team members:** Guandi Wang, Chentao Ye, Yang Qiu, Yuchen Liu

##### **Project Description:**

We have built a photo-based social media platform with the ability of meta-data searching and user interactions. The platform will enable users to upload, view, and interact with photos. It leveraged Amazon S3 for photo storage and utilize AWS RDS for data management and scalability.
Our platform consists of a client-side for user interactions, a server-side to handle requests from the client-side, and interactions with AWS S3 and AWS RDS.
Users will need to register and log in to access our platform’s key features. After logging in, users can upload photos to the platform. All uploaded photos will be public to all users by default. Users can view and interact with all photos on the platform. We also incorporated searching/sorting by metadata features (like counts, distance to a location), so that users can quickly find their target photo.

- Register/Login: Users can create an account and log in to access the app.
- Upload/Share Photos: Registered users can upload and share photos and its location with others.
- Swipe to Browse Photos: Users can intuitively browse through uploaded photos by swiping up and down.
- Like/Dislike: Users can express their preferences by liking or disliking photos shared within the app.
- Sort/Search Photos: Users can search and sort photos based on the number of likes or their proximity to a specific address.
- Geocode API Integration: Utilize an API to fetch geocode information, allowing users to associate their photos with specific locations.

##### **Project Architecture Diagram:**

![Imgur](https://i.imgur.com/4oPdbVN.jpg)



##### **Dataset ER Diagram:**

![Imgur](https://i.imgur.com/mfYrT9k.jpg)



