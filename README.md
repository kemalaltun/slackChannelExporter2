**Nasıl Çalışır?**
Token, Cookie ve Channel id bilgilerini **config.json** dosyasına eklememiz gerekiyor.

**Bu bilgilere nereden ulaşırım?**
1.Channel url'indeki son path bizim channel id'mizdir. veya Channel linki kopyalayarak linkteki id'yi alabilirsiniz
2.Token ve Cookie için network kısmına conversion.history yazalım ve ilgili channel'da sayfayı yenileyelim. Buradaki network isteğini curl olarak kopyalayıp postmane yapıştıralım.
![image](https://github.com/user-attachments/assets/1e605e56-8708-4feb-ac60-ca9830582d6f)
3.Bu curl'ü postman'e importlayalım.
4. Token bilgisine body kısmından ulaşabiliriz örn -> "xoxc-.." ![image](https://github.com/user-attachments/assets/44e9fa4a-bdd2-4ca6-ade3-c0e5f78578b1)
5. Cookie bilgisine Headers kısmından ulaşabiliriz örn -> "d=xoxd..." ![image](https://github.com/user-attachments/assets/e6f31f8e-48ac-4e26-847f-e562c3d14e48)

**messagesExportWithoutReplies.py**
Slack channel'ındaki tüm mesajları **thread.csv** dosyası olarak exportlar. reply kısımları dahil değildir

**threadsExportWithoutReplies.py**
Slack channel'ındaki tüm threadleri(altında reply içeren mesajlar) **thread.csv** dosyasına exportlar reply kısımları dahil değildir.

**repliesExport.py**
Slack channel'ındaki replies kısımlarını **thread.csv** dosyasındaki **thread_ts** fieldına göre **replies.csv** dosyasına exportlar. Çalışması için **thread.csv**'nin oluşmuş olması yani yukarıdaki 2 komuttan birinin çalıştırılmış olması gerekmektedir.
