import json
import os


HR_QA_DATA = [
    {
        "instruction": "What is the primary purpose of an employee onboarding program?",
        "input": "",
        "output": (
            "The primary purpose of an employee onboarding program is to integrate new hires "
            "into the organization by familiarizing them with company culture, policies, procedures, "
            "and their specific role responsibilities, while ensuring they have the resources and "
            "support needed to become productive and engaged team members."
        ),
    },
    {
        "instruction": "How can HR effectively manage remote employees?",
        "input": "",
        "output": (
            "HR can effectively manage remote employees by establishing clear communication channels, "
            "setting expectations for work hours and deliverables, providing necessary technology and "
            "resources, fostering a sense of inclusion through virtual team-building activities, "
            "offering regular check-ins and feedback, and ensuring access to professional development "
            "opportunities. Additionally, promoting work-life balance and addressing any challenges "
            "unique to remote work are essential."
        ),
    },
    {
        "instruction": "How does an HR department support employee well-being?",
        "input": "",
        "output": (
            "An HR department supports employee well-being by implementing programs and policies that "
            "promote physical, mental, and emotional health. This includes offering health benefits, "
            "wellness initiatives, work-life balance options, mental health resources, employee "
            "assistance programs, and fostering a positive workplace culture that encourages open "
            "communication and support."
        ),
    },
    {
        "instruction": "Define what constitutes a competitive compensation package.",
        "input": "",
        "output": (
            "A competitive compensation package includes base salary aligned with market rates, "
            "performance-based bonuses or incentives, comprehensive health and wellness benefits, "
            "retirement savings plans with employer contributions, paid time off, professional "
            "development opportunities, and additional perks that attract and retain talent in the "
            "relevant industry and geographic market."
        ),
    },
    {
        "instruction": "What are the key components of an effective performance review?",
        "input": "",
        "output": (
            "Key components of an effective performance review include clear evaluation criteria "
            "tied to job responsibilities, specific examples of accomplishments and areas for "
            "improvement, measurable goals and objectives, two-way dialogue between manager and "
            "employee, documentation of the discussion, and an action plan for future development "
            "and growth."
        ),
    },
    {
        "instruction": "Explain the difference between exempt and non-exempt employees.",
        "input": "",
        "output": (
            "Exempt employees are salaried workers who meet specific criteria under the Fair Labor "
            "Standards Act and are not entitled to overtime pay, typically holding executive, "
            "professional, or administrative positions. Non-exempt employees are entitled to overtime "
            "pay at one and a half times their regular rate for hours worked beyond 40 in a workweek "
            "and are usually paid hourly."
        ),
    },
    {
        "instruction": "What is the purpose of an exit interview?",
        "input": "",
        "output": (
            "The purpose of an exit interview is to gather feedback from departing employees about "
            "their experiences, reasons for leaving, workplace conditions, management effectiveness, "
            "and suggestions for improvement. This information helps organizations identify trends, "
            "address systemic issues, improve retention strategies, and enhance the overall employee "
            "experience."
        ),
    },
    {
        "instruction": "What does DEI stand for in HR context?",
        "input": "",
        "output": (
            "DEI stands for Diversity, Equity, and Inclusion. It represents organizational efforts "
            "to create a workplace that values different backgrounds and perspectives, ensures fair "
            "treatment and access to opportunities for all employees, and fosters a culture where "
            "everyone feels welcomed, respected, and able to contribute fully."
        ),
    },
    {
        "instruction": "What is the probationary period for new employees?",
        "input": "",
        "output": (
            "A probationary period is typically a 30 to 90-day initial employment phase during which "
            "new hires are evaluated on their performance, cultural fit, and ability to meet job "
            "requirements. During this time, either the employer or employee may terminate the "
            "relationship with minimal notice, and some benefits may be restricted until successful "
            "completion of the probationary period."
        ),
    },
    {
        "instruction": "Explain what constructive dismissal means.",
        "input": "",
        "output": (
            "Constructive dismissal occurs when an employer makes significant unilateral changes to "
            "an employee's working conditions, compensation, or responsibilities that effectively "
            "force the employee to resign. The changes are so substantial that they breach the "
            "employment contract, making continued employment unreasonable, even though the employer "
            "has not formally terminated the employee."
        ),
    },
    {
        "instruction": "What is the difference between a layoff and termination for cause?",
        "input": "",
        "output": (
            "A layoff is the separation of an employee due to business needs such as restructuring, "
            "downsizing, or economic conditions, not related to the employee's performance or conduct. "
            "Termination for cause is the dismissal of an employee due to policy violations, poor "
            "performance, misconduct, or behavior that breaches the employment agreement or company "
            "standards."
        ),
    },
    {
        "instruction": "What are protected characteristics under employment discrimination laws?",
        "input": "",
        "output": (
            "Protected characteristics typically include race, color, national origin, religion, sex, "
            "gender identity, sexual orientation, age (40 and over), disability, genetic information, "
            "pregnancy, and veteran status. Employers cannot make employment decisions based on these "
            "characteristics, and employees are protected from discrimination and harassment related "
            "to these attributes."
        ),
    },
    {
        "instruction": "Define what a PIP is in performance management.",
        "input": "",
        "output": (
            "A PIP (Performance Improvement Plan) is a formal document that outlines specific "
            "performance deficiencies, sets clear and measurable goals for improvement, establishes "
            "a timeline for achieving those goals, and describes the support and resources the "
            "employer will provide. It serves as a structured process to help underperforming "
            "employees meet job expectations or document ongoing performance issues."
        ),
    },
    {
        "instruction": "What is the purpose of workplace diversity training?",
        "input": "",
        "output": (
            "Workplace diversity training aims to educate employees about different cultures, "
            "backgrounds, and perspectives, reduce unconscious bias, promote inclusive behaviors, "
            "prevent discrimination and harassment, improve communication across diverse teams, and "
            "create a more respectful and equitable work environment where all employees can thrive."
        ),
    },
    {
        "instruction": "Explain what at-will employment means.",
        "input": "",
        "output": (
            "At-will employment means that either the employer or employee can terminate the "
            "employment relationship at any time, for any lawful reason or no reason at all, with or "
            "without notice. However, this is subject to exceptions including employment contracts, "
            "collective bargaining agreements, and legal protections against discrimination, "
            "retaliation, and violations of public policy."
        ),
    },
    {
        "instruction": "What is the primary goal of employee engagement initiatives?",
        "input": "",
        "output": (
            "The primary goal of employee engagement initiatives is to create an environment where "
            "employees feel emotionally committed to the organization, motivated to contribute their "
            "best work, connected to the company's mission and values, and satisfied with their work "
            "experience, ultimately leading to improved productivity, retention, and organizational "
            "performance."
        ),
    },
    {
        "instruction": "What is a non-disclosure agreement in employment?",
        "input": "",
        "output": (
            "A non-disclosure agreement (NDA) is a legal contract between an employer and employee "
            "that prohibits the employee from sharing confidential company information, trade secrets, "
            "proprietary data, or sensitive business information with outside parties during and often "
            "after their employment, protecting the organization's competitive advantages and "
            "intellectual property."
        ),
    },
    {
        "instruction": "Explain the concept of pay equity.",
        "input": "",
        "output": (
            "Pay equity refers to the principle of providing equal compensation to employees who "
            "perform substantially similar work, requiring comparable skills, effort, and "
            "responsibility under similar working conditions, regardless of gender, race, or other "
            "protected characteristics. It addresses systemic wage gaps and ensures fair compensation "
            "practices across the organization."
        ),
    },
    {
        "instruction": "What is the role of an HR business partner?",
        "input": "",
        "output": (
            "An HR business partner serves as a strategic advisor to business leaders, aligning HR "
            "initiatives with organizational goals, providing guidance on talent management, workforce "
            "planning, employee relations, and organizational development. They bridge the gap between "
            "HR functions and business units, delivering data-driven insights and solutions to drive "
            "business performance."
        ),
    },
    {
        "instruction": "What constitutes workplace harassment?",
        "input": "",
        "output": (
            "Workplace harassment is unwelcome conduct based on protected characteristics such as "
            "race, gender, religion, age, or disability that creates an intimidating, hostile, or "
            "offensive work environment. It includes verbal, physical, or visual behavior that is "
            "severe or pervasive enough to interfere with an individual's work performance or create "
            "an abusive working environment."
        ),
    },
    {
        "instruction": "What is the purpose of a job description?",
        "input": "",
        "output": (
            "A job description serves to clearly define the duties, responsibilities, required "
            "qualifications, skills, and reporting relationships for a specific position. It is used "
            "for recruitment, setting performance expectations, determining compensation levels, "
            "conducting performance evaluations, ensuring legal compliance, and helping employees "
            "understand their role within the organization."
        ),
    },
    {
        "instruction": "Explain what FMLA stands for and its purpose.",
        "input": "",
        "output": (
            "FMLA stands for the Family and Medical Leave Act, which provides eligible employees "
            "with up to 12 weeks of unpaid, job-protected leave per year for specified family and "
            "medical reasons, including the birth or adoption of a child, caring for a family member "
            "with a serious health condition, or the employee's own serious health condition. It "
            "ensures employees can address important family and health needs without losing their jobs."
        ),
    },
    {
        "instruction": "What is succession planning in HR?",
        "input": "",
        "output": (
            "Succession planning is the strategic process of identifying and developing internal "
            "employees to fill key leadership and critical positions when they become vacant due to "
            "retirement, promotion, or departure. It ensures business continuity, reduces talent gaps, "
            "maintains organizational knowledge, and prepares high-potential employees for future "
            "roles through targeted development."
        ),
    },
    {
        "instruction": "What are the main components of total compensation?",
        "input": "",
        "output": (
            "Total compensation includes direct compensation (base salary, bonuses, commissions, "
            "profit sharing), indirect compensation (health insurance, retirement contributions, paid "
            "time off, life and disability insurance), and other benefits (professional development, "
            "flexible work arrangements, wellness programs, employee assistance programs, and various "
            "perks). Together, these components represent the complete value an employee receives."
        ),
    },
    {
        "instruction": "What is the difference between recruitment and talent acquisition?",
        "input": "",
        "output": (
            "Recruitment is a tactical, reactive process focused on filling immediate job openings "
            "quickly and efficiently. Talent acquisition is a strategic, proactive approach that "
            "involves long-term workforce planning, building talent pipelines, employer branding, "
            "creating candidate relationships, and continuously seeking top talent to meet current "
            "and future organizational needs."
        ),
    },
    {
        "instruction": "Explain what unconscious bias is in the workplace.",
        "input": "",
        "output": (
            "Unconscious bias refers to automatic, implicit attitudes or stereotypes that affect our "
            "understanding, decisions, and actions without our conscious awareness. In the workplace, "
            "these biases can influence hiring decisions, performance evaluations, promotions, and "
            "daily interactions, potentially leading to unfair treatment and limiting diversity "
            "despite individuals' intentions to be fair and objective."
        ),
    },
    {
        "instruction": "What is the purpose of a 360-degree feedback process?",
        "input": "",
        "output": (
            "A 360-degree feedback process gathers performance feedback from multiple sources "
            "including supervisors, peers, direct reports, and sometimes clients or customers, in "
            "addition to self-assessment. This comprehensive approach provides a well-rounded view "
            "of an employee's strengths and development areas, reduces bias, increases self-awareness, "
            "and supports more effective professional development."
        ),
    },
    {
        "instruction": "What does it mean to be an equal opportunity employer?",
        "input": "",
        "output": (
            "Being an equal opportunity employer means the organization is committed to fair "
            "employment practices that do not discriminate based on race, color, religion, sex, "
            "national origin, age, disability, genetic information, or other protected characteristics. "
            "These employers make hiring, promotion, compensation, and other employment decisions "
            "based solely on qualifications, merit, and business needs."
        ),
    },
    {
        "instruction": "What is employee turnover and why does it matter?",
        "input": "",
        "output": (
            "Employee turnover is the rate at which employees leave an organization and are replaced "
            "by new hires, calculated as the percentage of employees who exit during a specific "
            "period. It matters because high turnover is costly due to recruitment expenses, training "
            "investments, lost productivity, decreased morale, and loss of institutional knowledge, "
            "while also potentially indicating underlying organizational issues."
        ),
    },
    {
        "instruction": "Explain what a collective bargaining agreement is.",
        "input": "",
        "output": (
            "A collective bargaining agreement is a written contract negotiated between an employer "
            "and a labor union representing employees that outlines terms and conditions of employment "
            "including wages, hours, benefits, workplace safety, grievance procedures, and other "
            "working conditions. It is legally binding and governs the employment relationship for "
            "the duration specified in the agreement."
        ),
    },
    # -----------------------------------------------------------------------
    # Additional records (new entries not in the original sample)
    # -----------------------------------------------------------------------
    {
        "instruction": "What is the purpose of an HR audit?",
        "input": "",
        "output": (
            "An HR audit is a systematic review of an organization's HR policies, procedures, "
            "documentation, and practices to ensure compliance with employment laws and regulations, "
            "identify gaps or inefficiencies, and align HR activities with business objectives. "
            "It helps organizations mitigate legal risks, improve HR processes, and enhance overall "
            "workforce management effectiveness."
        ),
    },
    {
        "instruction": "How is an employee assistance program (EAP) beneficial?",
        "input": "",
        "output": (
            "An employee assistance program (EAP) provides confidential counseling, referrals, and "
            "support services to employees facing personal or work-related challenges such as stress, "
            "substance abuse, mental health issues, financial difficulties, or family problems. "
            "EAPs improve employee well-being, reduce absenteeism, increase productivity, and "
            "demonstrate organizational care for employees' holistic health."
        ),
    },
    {
        "instruction": "What is the difference between job enrichment and job enlargement?",
        "input": "",
        "output": (
            "Job enrichment increases the depth of a role by adding greater responsibility, autonomy, "
            "and opportunities for skill development, making work more meaningful and challenging. "
            "Job enlargement expands the scope of a role horizontally by adding more tasks of a "
            "similar level, increasing variety without necessarily adding complexity or authority. "
            "Both strategies aim to improve employee motivation and reduce monotony."
        ),
    },
    {
        "instruction": "What are the main objectives of compensation management?",
        "input": "",
        "output": (
            "The main objectives of compensation management are to attract and retain qualified "
            "talent, motivate employees to perform at their best, ensure internal equity by paying "
            "employees fairly relative to one another, maintain external competitiveness by aligning "
            "pay with market rates, comply with legal requirements, and control labor costs within "
            "the organization's budget constraints."
        ),
    },
    {
        "instruction": "Explain the concept of employer of record (EOR).",
        "input": "",
        "output": (
            "An employer of record (EOR) is a third-party organization that legally employs workers "
            "on behalf of another company, handling payroll, tax compliance, benefits administration, "
            "and employment contracts. EOR services enable businesses to hire employees in new "
            "geographies quickly without establishing a legal entity, reducing administrative burden "
            "and ensuring compliance with local labor laws."
        ),
    },
    {
        "instruction": "What is the significance of psychological safety in the workplace?",
        "input": "",
        "output": (
            "Psychological safety is the belief that employees can speak up, share ideas, admit "
            "mistakes, or raise concerns without fear of punishment, ridicule, or negative consequences. "
            "It is critical for fostering innovation, collaboration, and continuous learning, enabling "
            "teams to take calculated risks, improve performance, address problems openly, and build "
            "stronger interpersonal trust within the organization."
        ),
    },
    {
        "instruction": "What is the role of HR analytics in decision-making?",
        "input": "",
        "output": (
            "HR analytics involves the collection, analysis, and interpretation of workforce data to "
            "support evidence-based decision-making in areas such as recruitment, retention, "
            "performance management, compensation, and workforce planning. By identifying trends, "
            "predicting outcomes, and measuring HR program effectiveness, organizations can make "
            "more informed strategic decisions that improve business performance and employee "
            "experience."
        ),
    },
    {
        "instruction": "What is the purpose of a job evaluation?",
        "input": "",
        "output": (
            "A job evaluation is a systematic process for determining the relative worth of jobs "
            "within an organization by analyzing and comparing the skills, effort, responsibility, "
            "and working conditions associated with each role. It establishes a rational basis for "
            "a fair and equitable pay structure, supports compensation decisions, ensures internal "
            "pay equity, and helps organizations benchmark roles against the external labor market."
        ),
    },
    {
        "instruction": "Explain the difference between a fixed-term and permanent employment contract.",
        "input": "",
        "output": (
            "A fixed-term contract is an employment agreement with a defined start and end date, "
            "often used for project-based work, seasonal demand, or to cover employee absences. "
            "A permanent contract has no predetermined end date and continues until terminated by "
            "either party. Permanent employees typically receive more comprehensive benefits and "
            "greater job security compared to fixed-term workers."
        ),
    },
    {
        "instruction": "What is absenteeism and how can HR address it?",
        "input": "",
        "output": (
            "Absenteeism refers to the habitual or frequent absence of employees from work beyond "
            "what is considered acceptable, which can reduce productivity and increase costs. HR can "
            "address absenteeism by identifying root causes through data analysis and employee "
            "conversations, implementing wellness programs, offering flexible work arrangements, "
            "ensuring fair workloads, recognizing attendance, and applying consistent leave "
            "management policies."
        ),
    },
]


def generate_raw_jsonl(output_path: str = "data/raw.jsonl") -> None:
    """Write HR Q&A records to a JSONL file at *output_path*."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for record in HR_QA_DATA:
            line = json.dumps(record, ensure_ascii=False)
            f.write(line + "\n")

    print(f"{len(HR_QA_DATA)} records → {output_path}")


if __name__ == "__main__":
    generate_raw_jsonl()