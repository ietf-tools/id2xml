/*
,----
| 
|   FILE: agenda_objects.js
|    
|   AUTHOR: Justin Hornosty ( justin@credil.org ) 
|     Orlando Project <-> Credil, 2012 ( credil.org )
|   
|   Description: 
|      Contains the objects relating to django's models. 
|      Manulaption and helper functions are also located here.
|      Display logic should be contained in credil_agenda.js ( this should be renamed )
|
`----
*/


function slot(){
    


}


function event_obj(title,description,room, time,date,django_id,session_id){
    this.title = title;
    this.description = description;
    this.room = room;
    this.time = time;
    this.date = date;
    this.django_id = django_id;
    this.session_id = session_id
}
