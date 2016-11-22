#Latex-access NVDA Addon:
This addon brings the full power of the [latex-access](http://latex-access.sourceforge.net/) engine to NVDA. Based on initial work by Nathaniel Schmidt, this plugin originally had the la tex processor and matrix processor implemented. It however was not very easy to use as you had to use complicated commands to move around the matrix, and could only store one matrix at a time in the software.
As a college student who took  calculus and linear algebra, and with an interest in math accessibility, I decided to improve upon these scripts. This script includes the ability to read la tex translated by NVDA, and allows users to save any amount of matrices into a buffer for viewing. The user can then easily navigate each  matrix with arrow keys, and move between matrices with the tab key. Future work may include allowing a user to add a new matrix, and spit out la tex into the current document or onto the clipboard ready for pasting. Work on the preprocessor is planned, so that users can add custom symbols to latex-access, as well as better support for braille. Also, it would be nice to bind other keys to the moving around scripts, so that la tex is spoken in all fields, not just editable fields. The plugin calls into latex-access automatically, and is pre-bundled with it, so that no COM server need be registered. I haven't figured out an easy way to register a com server while installing the plugin, and went with directly calling in since its easier and faster. The disadvantage is that new versions of latex-access must be manually bundled. I hope to work with the latex-access project to see if they will accept this addon back in, in which case, I can write scripts to create the addon for each new version of latex-access.

## 1: Keyboard shortcuts Quick reference:
### 1.0: Available in any Edit Field.
* control+nvda+shift+m: toggle processing of la tex on or off. Read section 3.0 for more details.
* control+nvda+shift+d: Toggle the presence of the $ sign around math in braille. Read 3.1 for more details.
* alt+nvda+shift+d: Toggle the presence of the $ sign around math in speech. Read 3.2 for more details.
* Alt+nvda+m: Add the currently selected matrix to the matrix browser. See 2.0: Matrices for a detailed tutorial.
* Alt+nvda+b: Show the matrix browser. See 2.1 for detailed instructions on using the matrix browser, and 1.1 for gestures available here as a list.

### 1.1: Matrix Browser:

* any arrow key: Move in that direction through the currently focused matrix.
* Tab or Shift+tab: Move to the next or previous matrix loaded into the browser.
* Delete: Deletes the current matrix.
* NVDA+Tab: Report the currently focused matrix.

## 2: matrix Browser: An overview.

### 2.0: Matrix Browser Tutorial

Assume you are working on a matrix multiplication problem. You have the following la tex.
```
$\begin{Bmatrix}
1&2&3\\
4 & 6 & 8
\end{Bmatrix} \times \begin{Bmatrix}
8 & 5 \\
7 & 3 \\
1 & 8 
\end{Bmatrix}$
```

You may find it difficult to arrow around the document from matrix to matrix while editing. To help with this problem, you need to load each matrix into your matrix browser.

1. Copy the above equation into a text editor. Not Microsoft word, notepad or something more feature rich. Ed Sharp or Notepad++ work great, and there's an nvda addon for notepad++.
2. Select the meet of matrix one, from the 1, until the 8. Don't select the surrounding \begin and \end tags.
3. Press nvda+shift+m. If you did it correctly you should hear "initialised 3 by 2 matrix"
4. Now, go down to matrix 2, and repeat the selection, pressing nvda+alt+m again. You should hear "initialised 2 by 3 matrix.
5. Type out your answer matrix, but don't fill it in. E.G. 
	```
	\begin{Bmatrix}
	
	\end{BMatrix}
	```
6. Now, put the cursor in the blank space in the equation. Press nvda+alt+b, read row one of matrix 1, and column 1 of matrix two. Type the multiplication out. You can type your answer out without leaving the matrix at all!!!

answer:

```
$\begin{Bmatrix}
8+14+3 & 5+6+24 \\
32+42+8 & 20+18+64
\end{BMatrix}= \begin{Bmatrix}
25 & 35 \\
82 & 102
\end{BMatrix}
```

### 2.1: Matrix Browser explained.

Now that you understand when this feature is useful, I'll give a more conventional description of how to use it.
You load selected matrix text into the browser with nvda+alt+m, which reports the matrix.
repeat that as many times as useful.
When you need to recall the matrix, press nvda+alt+b, and the matrix browser comes up.
Read the current matrix by arrowing around it, I.E. press right arrow to go to column 2. 
Pressing tab or shift+tab moves you to the previous or next matrix. Each matrix is numbered from 1 to n, and matrices renumber themselves when one is deleted.
Press delete to delete any arbitrary matrix. The next matrix is focused. Additionally, the matrices are renumbered to reflect the deletion.
Press escape to leave the browser.
If you need the matrix read again, simply press nvda+tab, which is NVDA's command to read the current focus.
To read the location in the matrix, press nvda+delete (The report location command). 

## 3: La tex reporting

### 3.0: La Tex Translation.

You can press nvda+shift+control+m to trigger la tex reporting. While on, this translates math to english speech and nemeth braille. For example, $x+\left(2 \cdot x\right)^2$ is translated to x plus   (2   dot  x  ) squared and brailled in nemeth, ⠭⠷⠆⠭⠾⠘⠆

### 3.1: Dollar signs in nemeth:
NVDA+shift+control+d toggles $ (dollar) signs in nemeth. If on, they show up, if off, they don't.

### 3.2: Dollar signs for speech:
NVDA+shift+alt+d toggles $ (dollar) signs in speech. If on, they are announced, if off, they don't.