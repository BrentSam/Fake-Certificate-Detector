# Literature Survey

This survey supports the first prototype: certificate image forgery screening
with Error Level Analysis (ELA) preprocessing and a small CNN classifier.

## Source 1

- Title: A Picture's Worth: Digital Image Analysis and Forensics
- Authors: Neal Krawetz
- Year: 2007
- Link or citation: https://www.hackerfactor.com/papers/bh-usa-07-krawetz-wp.pdf
- Method used: Practical image forensics techniques, including ELA-style JPEG recompression comparison.
- Dataset used: Demonstration examples rather than a formal benchmark dataset.
- Strengths: Introduces the intuition that JPEG recompression can expose regions with different compression histories.
- Limitations: ELA is visually interpretable but subjective when used alone, and it depends heavily on JPEG history and image quality.
- Relevance to this project: Provides the preprocessing idea used by `ela_converter.py`.

## Source 2

- Title: Image Forgery Localization via Block-Grained Analysis of JPEG Artifacts
- Authors: Tiziano Bianchi and Alessandro Piva
- Year: 2012
- Link or citation: https://doi.org/10.1109/TIFS.2012.2187516
- Method used: JPEG artifact and double-compression analysis to estimate likely forged regions.
- Dataset used: Realistic tampered image scenarios and JPEG forensic test cases.
- Strengths: Gives a stronger statistical foundation for using compression artifacts as forensic evidence.
- Limitations: Focuses on JPEG artifact assumptions and localization, not certificate-level classification.
- Relevance to this project: Supports the idea that tampering can leave compression traces, which the ELA image attempts to surface.

## Source 3

- Title: Constrained Convolutional Neural Networks: A New Approach Towards General Purpose Image Manipulation Detection
- Authors: Belhassen Bayar and Matthew C. Stamm
- Year: 2018
- Link or citation: https://doi.org/10.1109/TIFS.2018.2825953
- Method used: CNN with a constrained convolutional layer designed to suppress semantic image content and learn manipulation traces.
- Dataset used: Multiple image manipulation experiments across editing operations and camera conditions.
- Strengths: Shows why CNNs for forensics should learn low-level manipulation traces, not just object content.
- Limitations: The method is more advanced than this beginner prototype and requires careful dataset design.
- Relevance to this project: Justifies using a CNN after tamper-sensitive preprocessing.

## Source 4

- Title: Learning Rich Features for Image Manipulation Detection
- Authors: Peng Zhou, Xintong Han, Vlad I. Morariu, and Larry S. Davis
- Year: 2018
- Link or citation: https://openaccess.thecvf.com/content_cvpr_2018/html/Zhou_Learning_Rich_Features_CVPR_2018_paper.html
- Method used: Two-stream Faster R-CNN using RGB features and noise features for manipulation localization.
- Dataset used: Four standard image manipulation datasets.
- Strengths: Demonstrates that combining visual and noise/artifact streams improves manipulation detection.
- Limitations: Targets localization with a larger model and standard benchmark images, not a small certificate dataset.
- Relevance to this project: Reinforces that artifact-focused signals can complement raw visual content.

## Source 5

- Title: Detection of Tool based Edited Images from Error Level Analysis and Convolutional Neural Network
- Authors: Abhishek Gupta, Raunak Joshi, and Ronald Laban
- Year: 2022
- Link or citation: https://arxiv.org/abs/2204.09075
- Method used: ELA preprocessing followed by CNN classification of authentic versus edited images.
- Dataset used: CASIA ITDE v2.
- Strengths: Closely matches the planned ELA plus CNN pipeline and reports training/validation accuracy over different epoch counts.
- Limitations: Uses a general image tampering dataset rather than internship certificate documents.
- Relevance to this project: Serves as the closest methodological baseline for the implementation in this repository.

## Source 6

- Title: Towards Robust Tampered Text Detection in Document Image: New Dataset and New Solution
- Authors: Chenfan Qu, Chongyu Liu, Yuliang Liu, Xinhong Chen, Dezhi Peng, Fengjun Guo, and Lianwen Jin
- Year: 2023
- Link or citation: https://openaccess.thecvf.com/content/CVPR2023/html/Qu_Towards_Robust_Tampered_Text_Detection_in_Document_Image_New_Dataset_CVPR_2023_paper.html
- Method used: Document Tampering Detector with frequency perception, multi-view decoding, and curriculum learning.
- Dataset used: DocTamper, a large document image tampering dataset.
- Strengths: Directly studies document text tampering, where edits can be visually subtle.
- Limitations: More complex than the current prototype and oriented toward tampered-region detection rather than binary certificate screening.
- Relevance to this project: Shows that document-specific forgery detection is harder than general image tampering and should be future scope.

## Source 7

- Title: Exposing Digital Forgeries by Detecting Duplicated Image Regions
- Authors: Alin C. Popescu and Hany Farid
- Year: 2004
- Link or citation: https://digitalcommons.dartmouth.edu/cs_tr/254/
- Method used: Block-based copy-move detection with PCA feature reduction and lexicographic matching.
- Dataset used: Credible forged image examples with noise and JPEG compression tests.
- Strengths: Establishes a classic passive image-forensics approach for duplicated-region detection.
- Limitations: Detects one forgery type and does not address text edits, seals, signatures, or certificate-level semantics.
- Relevance to this project: Provides background for future copy-move checks on repeated seals, stamps, or signatures.

## Research Gap

Existing work shows that JPEG artifacts, ELA-like preprocessing, noise features,
and CNNs can help detect image manipulation. However, internship certificates
are a narrow document domain with small text edits, repeated visual patterns,
and privacy-sensitive data. Public general-purpose forgery datasets do not fully
represent certificate-specific edits such as altered names, dates, seals, and
signatures.

This project addresses the gap with a small, local, privacy-safe workflow:

- Use ELA preprocessing to expose compression inconsistencies.
- Train a binary CNN with `real=0` and `fake=1`.
- Record precision, recall, F1-score, and confusion matrix, not accuracy alone.
- Treat the result as a screening signal rather than proof of authenticity.
- Keep future room for OCR, issuer verification, and document-tamper localization.
