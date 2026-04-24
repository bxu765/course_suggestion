import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import json
import subprocess
import os
import sys
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Detect platform and set appropriate colors
IS_MAC = sys.platform == 'darwin'

if IS_MAC:
    # macOS-friendly colors that work with system appearance
    BG_COLOR = "#f5f5f5"
    LABEL_BG = "#f5f5f5"
    TEXT_COLOR = "black"
    BUTTON_BG = "#007AFF"
    BUTTON_FG = "black"
    SUCCESS_COLOR = "#34C759"
    TEXT_BG = "white"
    TEXT_FG = "black"
    STATUS_BG = "#E5E5EA"
    STATUS_FG = "black"
    LINK_COLOR = "#007AFF"
    ACCENT_COLOR = "#FF9500"
    SECONDARY_TEXT = "#555555"
else:
    # Windows/Linux colors
    BG_COLOR = "#f0f0f0"
    LABEL_BG = "#f0f0f0"
    TEXT_COLOR = "black"
    BUTTON_BG = "#4CAF50"
    BUTTON_FG = "white"
    SUCCESS_COLOR = "#4CAF50"
    TEXT_BG = "white"
    TEXT_FG = "black"
    STATUS_BG = "#e0e0e0"
    STATUS_FG = "#333"
    LINK_COLOR = "#2196F3"
    ACCENT_COLOR = "#FF9800"
    SECONDARY_TEXT = "#666"



class CourseRecommenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Course Recommender")
        self.root.geometry("900x700")
        self.root.configure(bg=BG_COLOR)
        
        # Load model and data once
        self.model = None
        self.course_embeddings = None
        self.courses = None
        self.descriptions = None
        self.taken_courses = set()
        
        self.load_data()
        self.create_widgets()
    
    def load_data(self):
        """Load embeddings and course data"""
        try:
            self.course_embeddings = np.load('course_embeddings.npy')
            with open('course_ids.json', 'r') as f:
                data = json.load(f)
                self.courses = data['courses']
                self.descriptions = data['descriptions']
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load course data: {e}")
    
    def load_taken_courses(self):
        """Load taken courses from JSON if it exists"""
        self.taken_courses = set()
        try:
            if os.path.exists('taken_courses.json'):
                with open('taken_courses.json', 'r') as f:
                    taken_data = json.load(f)
                    self.taken_courses = set(taken_data.get('taken_courses', []))
        except Exception as e:
            messagebox.showwarning("Warning", f"Could not load taken courses: {e}")
    
    def create_widgets(self):
        """Create GUI elements"""
        # Title
        # title = tk.Label(self.root, text="Course Recommender System", font=("Arial", 18, "bold"), bg=LABEL_BG)
        title = tk.Label(self.root, text="Course Recommender System", font=("Arial", 18, "bold"), bg=LABEL_BG, fg=TEXT_COLOR)
        title.pack(pady=10)
        
        # Frame for inputs
        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        # Interests section
        # tk.Label(input_frame, text="Enter Your Interests:", font=("Arial", 12, "bold"), bg=LABEL_BG).pack(anchor=tk.W)
        tk.Label(input_frame, text="Enter Your Interests:", font=("Arial", 12, "bold"), bg=LABEL_BG, fg=TEXT_COLOR).pack(anchor=tk.W)
        # self.interests_text = tk.Text(input_frame, height=4, width=50, font=("Arial", 10), wrap=tk.WORD)
        self.interests_text = tk.Text(
            input_frame,
            height=4,
            width=50,
            font=("Arial", 10),
            wrap=tk.WORD,
            bg=TEXT_BG,
            fg=TEXT_FG,
            insertbackground=TEXT_FG
        )
        self.interests_text.pack(fill=tk.BOTH, pady=5)
        
        # Transcript upload section
        # tk.Label(input_frame, text="Upload Transcript (Optional):", font=("Arial", 12, "bold"), bg=LABEL_BG).pack(anchor=tk.W, pady=(15, 0))
        tk.Label(input_frame, text="Upload Transcript (Optional):", font=("Arial", 12, "bold"), bg=LABEL_BG, fg=TEXT_COLOR).pack(anchor=tk.W, pady=(15, 0)) 
        transcript_button_frame = tk.Frame(input_frame, bg=BG_COLOR)
        transcript_button_frame.pack(anchor=tk.W, pady=5)
        
        # tk.Button(transcript_button_frame, text="Select PDF", command=self.upload_transcript, 
        #          bg=BUTTON_BG, fg=BUTTON_FG, font=("Arial", 10), padx=10).pack(side=tk.LEFT, padx=5)
        tk.Button(
            transcript_button_frame,
            text="Select PDF",
            command=self.upload_transcript,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_BG,
            activeforeground=BUTTON_FG,
            highlightbackground=BG_COLOR,
            font=("Arial", 10, "bold"),
            padx=10
        ).pack(side=tk.LEFT, padx=5)
        
        self.transcript_label = tk.Label(transcript_button_frame, text="No file selected", 
                                        font=("Arial", 10), bg=LABEL_BG, fg=SECONDARY_TEXT)
        self.transcript_label.pack(side=tk.LEFT, padx=10)
        
        self.transcript_path = None
        
        # Button to find courses
        # tk.Button(self.root, text="Find Similar Courses", command=self.find_courses,
        #          bg=LINK_COLOR, fg=BUTTON_FG, font=("Arial", 12, "bold"), padx=20, pady=10).pack(pady=15)
        tk.Button(
            self.root,
            text="Find Similar Courses",
            command=self.find_courses,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            activebackground=BUTTON_BG,
            activeforeground=BUTTON_FG,
            highlightbackground=BG_COLOR,
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        ).pack(pady=15)
        
        # Results section
        # tk.Label(self.root, text="Top 5 Recommended Courses:", font=("Arial", 12, "bold"), bg=LABEL_BG).pack(anchor=tk.W, padx=20, pady=(10, 5))
        tk.Label(self.root, text="Top 5 Recommended Courses:", font=("Arial", 12, "bold"), bg=LABEL_BG, fg=TEXT_COLOR).pack(anchor=tk.W, padx=20, pady=(10, 5))
        
        # Results display with scrollbar
        results_frame = tk.Frame(self.root, bg=TEXT_BG, relief=tk.SUNKEN, bd=1)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, width=100, 
                                                     font=("Arial", 10), wrap=tk.WORD, bg=TEXT_BG, fg=TEXT_FG)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        self.results_text.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self.root, textvariable=self.status_var, font=("Arial", 9), 
                             bg=STATUS_BG, fg=STATUS_FG, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=0, pady=0)
    
    def upload_transcript(self):
        """Handle transcript upload"""
        file_path = filedialog.askopenfilename(
            title="Select Transcript PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.transcript_path = file_path
            filename = os.path.basename(file_path)
            self.transcript_label.config(text=f"Selected: {filename}", fg=SUCCESS_COLOR)
            self.status_var.set(f"Processing transcript: {filename}")
            self.root.update()
            
            try:
                # Run transcript parser using the current Python executable (which is in the venv)
                subprocess.run([
                    sys.executable, "transcript_parser.py", file_path
                ], check=True, capture_output=True, text=True)
                
                # Reload taken courses
                self.load_taken_courses()
                self.status_var.set(f"Transcript loaded successfully. Found {len(self.taken_courses)} courses.")
                messagebox.showinfo("Success", f"Transcript loaded!\nFound {len(self.taken_courses)} courses already taken.")
            except subprocess.CalledProcessError as e:
                self.status_var.set("Error processing transcript")
                error_msg = e.stderr if e.stderr else e.stdout
                messagebox.showerror("Error", f"Failed to process transcript:\n{error_msg}")
            except Exception as e:
                self.status_var.set("Error")
                messagebox.showerror("Error", f"An error occurred: {e}")
    
    def find_courses(self):
        """Find similar courses based on interests"""
        interests = self.interests_text.get("1.0", tk.END).strip()
        
        if not interests:
            messagebox.showwarning("Warning", "Please enter your interests.")
            return
        
        self.status_var.set("Loading model and calculating similarities...")
        self.root.update()
        
        try:
            # Load model lazily (only when needed)
            if self.model is None:
                self.status_var.set("Loading AI model (this may take a moment)...")
                self.root.update()
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            self.status_var.set("Searching for similar courses...")
            self.root.update()
            
            # Generate embedding for interests
            interest_embedding = self.model.encode([interests])[0]
            
            # Calculate cosine similarity
            similarities = cosine_similarity([interest_embedding], self.course_embeddings)[0]
            
            # Get top courses
            sorted_indices = np.argsort(similarities)[::-1]
            
            results = []
            for idx in sorted_indices:
                if self.courses[idx] not in self.taken_courses:
                    results.append({
                        'course_id': self.courses[idx],
                        'similarity': float(similarities[idx]),
                        'description': self.descriptions[idx]
                    })
                if len(results) >= 5:
                    break
            
            # Display results
            self.display_results(results, interests)
            self.status_var.set("Done!")
            
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", f"Failed to find courses: {e}")
    
    def display_results(self, results, interests):
        """Display results in the text widget"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete("1.0", tk.END)
        
        if not results:
            self.results_text.insert(tk.END, "No courses found. You may have already taken all similar courses!")
        else:
            for i, result in enumerate(results, 1):
                # Course info
                course_info = f"{i}. {result['course_id']}\n"
                self.results_text.insert(tk.END, course_info, "course_id")
                
                # Similarity score
                similarity_info = f"Similarity Score: {(result['similarity'] * 100):.2f}%\n"
                self.results_text.insert(tk.END, similarity_info, "similarity")
                
                # Parse description and prerequisites
                description = result['description']
                prerequisite = None
                
                if "Prerequisite" in description:
                    parts = description.split("Prerequisite")
                    description = parts[0].strip()
                    prerequisite = parts[1].strip()
                
                # Display description
                description_text = f"{description}\n"
                self.results_text.insert(tk.END, description_text, "description")
                
                # Display prerequisite if it exists
                if prerequisite:
                    prerequisite_text = f"Prerequisite{prerequisite}\n"
                    self.results_text.insert(tk.END, prerequisite_text, "prerequisite")
                
                self.results_text.insert(tk.END, "\n")
        
        # Configure tags for styling
        self.results_text.tag_config("course_id", font=("Arial", 12, "bold"), foreground=LINK_COLOR)
        self.results_text.tag_config("similarity", font=("Arial", 10), foreground=ACCENT_COLOR)
        self.results_text.tag_config("description", font=("Arial", 10), foreground=TEXT_COLOR)
        self.results_text.tag_config("prerequisite", font=("Arial", 10, "italic"), foreground=SECONDARY_TEXT)
        
        self.results_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = CourseRecommenderGUI(root)
    root.mainloop()
