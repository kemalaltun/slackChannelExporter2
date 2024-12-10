Nasıl Çalışır?
Token, Cookie ve Channel id bilgileri çalışması için yeterlidir

Bu bilgilere nereden ulaşırım?
1.Channel url'indeki son path bizim channel id'mizdir. veya Channel linki kopyalayarak linkteki id'yi alabilirsiniz
2.Token ve Cookie için network kısmına conversion.history yazalım ve ilgili channel'da sayfayı yenileyelim. Buradaki network isteğini curl olarak kopyalayıp postmane yapıştıralım.
![image](https://github.com/user-attachments/assets/274ae36a-6335-429d-98a9-2b1cc908de3d)
3.Bu curl'ü postman'e importlayalım.
4. Token bilgisine body kısmından ulaşabiliriz örn -> "xoxc-.." ![image](https://github.com/user-attachments/assets/04867e9a-e479-4e85-bd69-7bf0f8d92e67)
5. Cookie bilgisine Headers kısmından ulaşabiliriz örn -> "d=xoxd..." ![image](https://github.com/user-attachments/assets/039cfa2e-183d-4ede-b2fe-5736368f709e)

