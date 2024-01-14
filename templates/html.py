css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}


.chat-message .avatar {
  width: 10%;
}
.chat-message .avatar img {
  max-width: 50px;
  max-height: 50px;
  border-radius: 50%;
  border: 2px solid;
  object-fit: cover;
}
.chat-message .message {
  width: 95%;
  padding: 1.5rem;
  color: #fff;
  background-color: #0078FF;
  border-radius: 15px;
}
'''

user_template = '''
<div class="chat-message user">
    <div class="message">{{MSG}}</div>
     <div class="avatar">
        <img src="https://i.ibb.co/g6zNWpQ/pngegg.png " style="margin-left: 30%">
    </div>
</div>
'''


bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/xhTfqDb/artificial-intelligence-8025738-640.jpg">
    </div>    
    <div class="message" style="background-color: rgb(216,216,216); color: black">{{MSG}}</div>
</div>
'''
