# Wine Quality Predictor

In this project, a website will be created to do the following:
- Allow a quick wine quality prediction when wine properties are input into the website.
- Allow many wine quality predictions to be done when a csv file with all the wines properties is uploaded to the website.
- Record the past predictions made by user.

This website application can be used by a wine selling shop to purchase wine of higher quality before obtaining feedback from customers.Thus, increasing sales. It can also be use to select wine with higher quality for a specific customer. For example, the sales person can recommend wines with high predicted wine quality with low alcohol for a customer which prefers wine with lower alcohol level or wine with higher quality & higher pH for customers whom prefer wine that is less sour.

##### The project can be viewed from the link: https://wine-quality-predicting.herokuapp.com/ 

*Note: As the website and database is hosted by free services, the website may take longer than normal website when loading. As dataspace is limited due it being free, there is a limit of
100 user accounts and 9000 stored prediction data pre-set for the website. If 100 user account limit is reached, kindly login using the pre-registered account (user:testuser, password: pass). When 9000 prediction data limit is reached, prediction data will no longer be able to be stored. Hence, mass prediction can no longer work but quick prediction will still work but data will no longer be stored.

##### See ipynb file for model building of wine quality prediction. optimise model is saved as "model.bin"

---
# Summary of project

### CONTENT PAGE
 - [Register and login](#login)
 - [Home Page](#home)
 - [Quick prediction](#quick)
 - [Mass predictions](#mass)

### Website structure
```
website
|---Procfile
|---wsgi.py
|---requirements.txt
|---app.py
|---model.bin
|---templates
|      |-------db.yaml < Removed due to sensitive information >
|      |-------base.html
|      |-------register.html
|      |-------login.html
|      |-------home.html
|      |-------quick.html
|      |-------mass.html
|---static
|      |-------styles.css
|      |-------<images>
```

<a name="login"></a>
### Register and Login
First register for an account by going to the register page from the "register here" link on the login page.
After account has been created, login using created account. 
If number of user accounts is maxed out. Use the following testing account:
```
User: testuser
Password: pass
```
![image](https://drive.google.com/uc?export=view&id=1sUrYfWlT-ff4x1wGF3HnCMNRrFeto1i_)

After login, you will be able to see the home page. 
Access to website is denied if user is not logged in.
User can logout from the navigation bar after logging in or automatically logged out after 15 mins of inactivity.

---
<a name="home"></a>
### Home Page
The home page is the page users will see once they are logged in.
In this page, username and all past predictions made by user will be listed on this page.
The listing are user specific (users can only see their own predictions). 
Timestamp is also added to all past predictions.
Below shows the home page of user, testuser, after logging in. 
There is also one past prediction that is made on 7 Dec 2021.

![image](https://drive.google.com/uc?export=view&id=1PXnpBkJbBgzH27Eg8v_CV0oTIt6CKZWc)

---
<a name="quick"></a>
### Quick Prediction
Quick prediction page allows users to make individual prediction when properties of the wine is input on this page. 
The prediction of the wine quality will be shown on this page when input data is submitted. 
The prediction data will also be stored and can be seen from the home page.
Below shows the quick prediction page.

![image](https://drive.google.com/uc?export=view&id=1_nWut8Qjbx_YbmwDF2tAnfp7KIuerx0j)


---
<a name="mass"></a>
### Mass predictions
If many predictions have to be made, it can be done through the mass prediction tab which allows the upload of a CSV file with the properties of the wines stored. 
(see image below) The file "testing.csv" is an example of a file that can be uploaded on this page.
Input of data shall follow according to the image on the mass prediction page and in CSV format. 
Insert file and and upload it. When the data is uploaded, user will be redirected to the home page where the prediction data will be displayed. 
CSV file can be created with user friendly software like excel which most people are familiar with.
Below shows the mass prediction page.

![image](https://drive.google.com/uc?export=view&id=1VyEmJjLfFRJjzUw4FBfyjR1058t36gy-)

The following checks are done before the file can be uploaded:
1. Check that a file is attached.
2. Check that the file is of correct format.
3. Check that the database have not reached 9000 rows limit
4. Check that the column headers are of correct format.
5. Check that all data are filled.


