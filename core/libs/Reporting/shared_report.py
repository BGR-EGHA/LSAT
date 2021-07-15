import docx
import os


class shared_report():
    """
    This class bundles a few basic functions used by the other report generators.
    """

    def opentemplate():
        """
        Opens the LSAT Word template (core\\libs\\Reporting\\default.docx) and preps it for editing,
        by removing an empty line at the beginning.
        """
        templatepath = os.path.join(os.getcwd(), "core", "libs", "Reporting", "default.docx")
        doc = docx.Document(templatepath)
        # Workaround to remove empty line at the beginning
        p = doc.paragraphs[0]._element
        p.getparent().remove(p)
        p._p = p._element = None
        return doc

    def savedoc(outputname, project_path, doc, analysis) -> None:
        """
        Saves the document under results\\*analysis*\reports\\*outputname*.docx
        doc is the Document object
        """
        path = os.path.join(project_path, "results", analysis, "reports", outputname + ".docx")
        doc.save(path)
