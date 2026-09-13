from src.document_reader import read_pdf
from src.llm_client import extract_case_data


PDF_PATH = "inputs/case_information.pdf"


def main():
    print("================================")
    print("STEP 2: CASE INFORMATION TEST")
    print("================================\n")

    # Step 1 → Read PDF
    print("📄 Reading PDF...")
    text = read_pdf(PDF_PATH)

    print(f"✅ PDF read successfully")
    print(f"   Extracted characters: {len(text)}\n")

    # Step 2 → Extract structured information
    print("🤖 Extracting case information using LLM...")
    case_data = extract_case_data(text)

    print("✅ Case information extracted!\n")

    # Display structured result
    print("================================")
    print("EXTRACTED CASE DATA")
    print("================================")

    print(f"Court: {case_data.court}")
    print(f"Jurisdiction: {case_data.jurisdiction}")
    print(f"Proceeding: {case_data.proceeding}")
    print(f"Case Number: {case_data.case_number}")
    print(f"Year: {case_data.year}")
    print(f"Petitioner: {case_data.petitioner}")

    print("\nRespondents:")
    for respondent in case_data.respondents:
        print(
            f"  Respondent No. {respondent.respondent_number}: "
            f"{respondent.name}"
        )

    print(f"\nFiled on behalf of: {case_data.respondent_number}")

    print("\nDeponent:")
    print(f"  Name: {case_data.deponent}")
    print(f"  Designation: {case_data.designation}")
    print(f"  Organisation: {case_data.organisation}")
    print(f"  Address: {case_data.address}")
    print(f"  Verification verb: {case_data.verification_verb}")

    print("\nReply Points:")
    for point in case_data.reply_points:
        print(f"\n  Point {point.point_number}: {point.title}")

        for detail in point.details:
            print(f"    - {detail}")

    print(f"\nPrayer: {case_data.prayer}")

    print("\nAttestation:")
    print(f"  Place: {case_data.attestation_place}")
    print(f"  Date: {case_data.attestation_date}")

    print("\nAdvocate:")
    print(f"  Firm: {case_data.advocate.firm_name}")
    print(f"  Acting for: {case_data.advocate.acting_for}")

    print("\n================================")
    print("STEP 2 TEST COMPLETED")
    print("================================")


if __name__ == "__main__":
    main()