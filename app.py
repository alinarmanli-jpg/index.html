import time
import json
import os
from datetime import datetime

class StudyTask:
    """Çalışma görevlerini temsil eden sınıf."""
    def __init__(self, task_id: int, title: str, category: str = "Genel"):
        self.id = task_id
        self.title = title
        self.category = category
        self.completed = False
        self.created_at = datetime.now().strftime("%d.%m.%Y %H:%M")

    def toggle(self):
        """Görev durumunu değiştirir (Tamamlandı/Tamamlanmadı)."""
        self.completed = not self.completed

    def to_dict(self):
        """Görev verisini sözlük formatına çevirir."""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "completed": self.completed,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Sözlükten StudyTask nesnesi oluşturur."""
        task = cls(data["id"], data["title"], data.get("category", "Genel"))
        task.completed = data.get("completed", False)
        task.created_at = data.get("created_at", datetime.now().strftime("%d.%m.%Y %H:%M"))
        return task

    def __str__(self):
        status = "✓" if self.completed else " "
        return f"[{status}] #{self.id:02d} | [{self.category}] {self.title} ({self.created_at})"


class FocusStudio:
    """Focus Studio - Python Ders ve Çalışma Planlayıcısı Ana Sınıfı."""

    def __init__(self, data_file="focus_data.json"):
        self.data_file = data_file
        self.tasks = []
        self.next_task_id = 1
        self.xp = 0
        self.level = 1
        self.streak = 1
        self.completed_pomo_count = 0
        self.load_data()

    def load_data(self):
        """Kayıtlı verileri JSON dosyasından yükler."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.xp = data.get("xp", 0)
                    self.level = data.get("level", 1)
                    self.streak = data.get("streak", 1)
                    self.completed_pomo_count = data.get("completed_pomo_count", 0)
                    self.next_task_id = data.get("next_task_id", 1)
                    self.tasks = [StudyTask.from_dict(t) for t in data.get("tasks", [])]
            except Exception as e:
                print(f"[HATA] Veri yüklenirken sorun oluştu: {e}")

    def save_data(self):
        """Mevcut verileri JSON dosyasına kaydeder."""
        data = {
            "xp": self.xp,
            "level": self.level,
            "streak": self.streak,
            "completed_pomo_count": self.completed_pomo_count,
            "next_task_id": self.next_task_id,
            "tasks": [t.to_dict() for t in self.tasks]
        }
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[HATA] Veri kaydedilirken sorun oluştu: {e}")

    def add_xp(self, amount: int):
        """Kullanıcıya XP kazandırır ve seviye atlama durumunu kontrol eder."""
        self.xp += amount
        print(f"\n🌟 +{amount} XP Kazandınız! (Toplam XP: {self.xp})")
        
        required_xp = self.level * 100
        if self.xp >= required_xp:
            self.level += 1
            print(f"🎉 TEBRİKLER! Seviye atladınız! Yeni Seviye: {self.level}")
        
        self.save_data()

    def add_task(self, title: str, category: str = "Genel"):
        """Yeni bir çalışma görevi ekler."""
        task = StudyTask(self.next_task_id, title, category)
        self.tasks.append(task)
        self.next_task_id += 1
        print(f"\n[EKLENDİ] Görev #{task.id}: {title} [{category}]")
        self.add_xp(20)
        self.save_data()

    def toggle_task(self, task_id: int):
        """Görev tamamlanma durumunu değiştirir."""
        for task in self.tasks:
            if task.id == task_id:
                task.toggle()
                status_str = "Tamamlandı" if task.completed else "Tamamlanmadı olarak işaretlendi"
                print(f"\n[GÜNCELLENDİ] Görev #{task.id} {status_str}.")
                if task.completed:
                    self.add_xp(35)
                else:
                    self.save_data()
                return
        print("\n[HATA] Belirtilen ID ile görev bulunamadı!")

    def delete_task(self, task_id: int):
        """Bir görevi listeden siler."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                removed = self.tasks.pop(i)
                print(f"\n[SİLİNDİ] Görev #{removed.id}: {removed.title}")
                self.save_data()
                return
        print("\n[HATA] Belirtilen ID ile görev bulunamadı!")

    def list_tasks(self, filter_type: str = "all"):
        """Görevleri filtreli veya filtresiz şekilde listeler."""
        print("\n" + "=" * 50)
        print("         Focus Studio - Çalışma Görevleri")
        print("=" * 50)

        if not self.tasks:
            print("Henüz hiç görev eklenmemiş.")
            print("-" * 50)
            return

        filtered = self.tasks
        if filter_type == "active":
            filtered = [t for t in self.tasks if not t.completed]
        elif filter_type == "completed":
            filtered = [t for t in self.tasks if t.completed]

        if not filtered:
            print(f"Bu filtrede ({filter_type}) gösterilecek görev yok.")
        else:
            for task in filtered:
                print(task)

        completed_count = sum(1 for t in self.tasks if t.completed)
        print("-" * 50)
        print(f"Toplam Görev: {len(self.tasks)} | Tamamlanan: {completed_count} | İlerleme: %{int(completed_count/len(self.tasks)*100) if self.tasks else 0}")

    def start_pomodoro(self, minutes: int = 25):
        """Konsol tabanlı Pomodoro zamanlayıcısını çalıştırır."""
        seconds = minutes * 60
        print("\n" + "=" * 50)
        print(f"  🔥 Pomodoro Odak Seansı Başladı ({minutes} Dakika)")
        print("  Çıkmak için Ctrl+C tuşlarına basabilirsiniz.")
        print("=" * 50 + "\n")

        try:
            while seconds > 0:
                mins, secs = divmod(seconds, 60)
                timer_str = f"⏱️ Kalan Süre: {mins:02d}:{secs:02d}"
                print(timer_str, end="\r", flush=True)
                time.sleep(1)
                seconds -= 1

            print("\n\n🔔 SÜRE BİTTİ! Harika bir odaklanma seansı tamamladınız.")
            self.completed_pomo_count += 1
            self.add_xp(50)
            self.save_data()

        except KeyboardInterrupt:
            print("\n\n⚠️ Pomodoro seansı durduruldu.")

    def show_profile(self):
        """Kullanıcının genel profil durumunu ve istatistiklerini gösterir."""
        completed_tasks = sum(1 for t in self.tasks if t.completed)
        required_xp = self.level * 100

        print("\n" + "=" * 50)
        print("          Focus Studio - Kullanıcı Profili")
        print("=" * 50)
        print(f"🏆 Seviye           : {self.level}")
        print(f"⭐ Deneyim (XP)     : {self.xp} / {required_xp} XP")
        print(f"🔥 Seri             : {self.streak} Gün")
        print(f"⏱️ Tamamlanan Pomo  : {self.completed_pomo_count} Oturum")
        print(f"✅ Tamamlanan Görev : {completed_tasks} / {len(self.tasks)}")
        print("=" * 50)


def clear_screen():
    """Ekranı temizler (Windows / Linux / Mac uyumlu)."""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    studio = FocusStudio()

    while True:
        print("\n==================================================")
        print("      FOCUS STUDIO - PYTHON ÇALIŞMA PLANLAYICISI   ")
        print("==================================================")
        print(f" Level: {studio.level} | XP: {studio.xp} | Pomo: {studio.completed_pomo_count}")
        print("--------------------------------------------------")
        print("1. Görevleri Listele")
        print("2. Yeni Görev Ekle")
        print("3. Görev Durumunu Değiştir (Tamamla / Aç)")
        print("4. Görev Sil")
        print("5. Pomodoro Zamanlayıcı Başlat")
        print("6. Profil ve İstatistikleri Göster")
        print("7. Çıkış")
        print("--------------------------------------------------")

        choice = input("Seçiminiz (1-7): ").strip()

        if choice == "1":
            print("\n1. Tüm Görevler")
            print("2. Sadece Devam Edenler")
            print("3. Sadece Tamamlananlar")
            sub_choice = input("Listeleme türü seçin (1-3) [Varsayılan 1]: ").strip()
            
            if sub_choice == "2":
                studio.list_tasks("active")
            elif sub_choice == "3":
                studio.list_tasks("completed")
            else:
                studio.list_tasks("all")

        elif choice == "2":
            title = input("\nGörev Başlığı: ").strip()
            if not title:
                print("[UYARI] Görev başlığı boş bırakılamaz!")
                continue

            print("\nKategoriler: [1] Matematik  [2] Yazılım  [3] Dil  [4] Genel")
            cat_choice = input("Kategori Seçimi (1-4) [Varsayılan 4]: ").strip()
            category_map = {"1": "Matematik", "2": "Yazılım", "3": "Dil", "4": "Genel"}
            category = category_map.get(cat_choice, "Genel")

            studio.add_task(title, category)

        elif choice == "3":
            studio.list_tasks("all")
            try:
                task_id = int(input("\nDurumu değiştirilecek Görev ID: "))
                studio.toggle_task(task_id)
            except ValueError:
                print("[HATA] Lütfen geçerli bir sayı girin!")

        elif choice == "4":
            studio.list_tasks("all")
            try:
                task_id = int(input("\nSilinecek Görev ID: "))
                studio.delete_task(task_id)
            except ValueError:
                print("[HATA] Lütfen geçerli bir sayı girin!")

        elif choice == "5":
            try:
                pomo_mins = input("\nPomodoro Süresi (Dakika) [Varsayılan 25]: ").strip()
                mins = int(pomo_mins) if pomo_mins else 25
                studio.start_pomodoro(mins)
            except ValueError:
                print("[HATA] Geçersiz dakika değeri!")

        elif choice == "6":
            studio.show_profile()

        elif choice == "7":
            print("\nFocus Studio'dan çıkılıyor. Çalışmalarınızda başarılar dileriz! 🚀")
            break

        else:
            print("\n[HATA] Geçersiz seçim! Lütfen 1-7 arasında bir değer girin.")


if __name__ == "__main__":
    main()