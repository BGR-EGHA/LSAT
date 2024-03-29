# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\AdvancedSettingsLogReg.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AdvancedSettingsLogReg(object):
    def setupUi(self, AdvancedSettingsLogReg):
        AdvancedSettingsLogReg.setObjectName("AdvancedSettingsLogReg")
        AdvancedSettingsLogReg.resize(500, 480)
        self.horizontalLayout = QtWidgets.QHBoxLayout(AdvancedSettingsLogReg)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mainGridLayout = QtWidgets.QGridLayout()
        self.mainGridLayout.setObjectName("mainGridLayout")
        self.advancedSettingsGroupBox = QtWidgets.QGroupBox(AdvancedSettingsLogReg)
        self.advancedSettingsGroupBox.setObjectName("advancedSettingsGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.advancedSettingsGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.advancedSettingsGroupBoxGridLayout = QtWidgets.QGridLayout()
        self.advancedSettingsGroupBoxGridLayout.setObjectName("advancedSettingsGroupBoxGridLayout")
        self.interceptScaleLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.interceptScaleLineEdit.setObjectName("interceptScaleLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.interceptScaleLineEdit, 7, 1, 1, 1)
        self.inverseRegLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.inverseRegLabel.setObjectName("inverseRegLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.inverseRegLabel, 5, 0, 1, 1)
        self.inverseRegLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.inverseRegLineEdit.setObjectName("inverseRegLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.inverseRegLineEdit, 5, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.label.setObjectName("label")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.label, 6, 0, 1, 1)
        self.max_iterLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.max_iterLabel.setObjectName("max_iterLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.max_iterLabel, 10, 0, 1, 1)
        self.multi_classLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.multi_classLabel.setObjectName("multi_classLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.multi_classLabel, 11, 0, 1, 1)
        self.randomStateLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.randomStateLabel.setObjectName("randomStateLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.randomStateLabel, 9, 0, 1, 1)
        self.solverComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.solverComboBox.setObjectName("solverComboBox")
        self.solverComboBox.addItem("")
        self.solverComboBox.addItem("")
        self.solverComboBox.addItem("")
        self.solverComboBox.addItem("")
        self.solverComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.solverComboBox, 0, 1, 1, 1)
        self.penaltyLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.penaltyLabel.setObjectName("penaltyLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.penaltyLabel, 1, 0, 1, 1)
        self.interceptComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.interceptComboBox.setObjectName("interceptComboBox")
        self.interceptComboBox.addItem("")
        self.interceptComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.interceptComboBox, 6, 1, 1, 1)
        self.max_iterLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.max_iterLineEdit.setObjectName("max_iterLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.max_iterLineEdit, 10, 1, 1, 1)
        self.randomStateComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.randomStateComboBox.setObjectName("randomStateComboBox")
        self.randomStateComboBox.addItem("")
        self.randomStateComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.randomStateComboBox, 9, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.advancedSettingsGroupBoxGridLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.penaltyComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.penaltyComboBox.setObjectName("penaltyComboBox")
        self.penaltyComboBox.addItem("")
        self.penaltyComboBox.addItem("")
        self.penaltyComboBox.addItem("")
        self.penaltyComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.penaltyComboBox, 1, 1, 1, 1)
        self.solverLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.solverLabel.setObjectName("solverLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.solverLabel, 0, 0, 1, 1)
        self.classWeightLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.classWeightLabel.setObjectName("classWeightLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.classWeightLabel, 8, 0, 1, 1)
        self.randomStateLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.randomStateLineEdit.setObjectName("randomStateLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.randomStateLineEdit, 9, 2, 1, 1)
        self.interceptScaleLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.interceptScaleLabel.setObjectName("interceptScaleLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.interceptScaleLabel, 7, 0, 1, 1)
        self.multi_classComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.multi_classComboBox.setObjectName("multi_classComboBox")
        self.multi_classComboBox.addItem("")
        self.multi_classComboBox.addItem("")
        self.multi_classComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.multi_classComboBox, 11, 1, 1, 1)
        self.classWeightComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.classWeightComboBox.setObjectName("classWeightComboBox")
        self.classWeightComboBox.addItem("")
        self.classWeightComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.classWeightComboBox, 8, 1, 1, 1)
        self.toleranceLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.toleranceLabel.setObjectName("toleranceLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.toleranceLabel, 4, 0, 1, 1)
        self.dualLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.dualLabel.setObjectName("dualLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.dualLabel, 3, 0, 1, 1)
        self.toleranceLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.toleranceLineEdit.setObjectName("toleranceLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.toleranceLineEdit, 4, 1, 1, 1)
        self.dualComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.dualComboBox.setObjectName("dualComboBox")
        self.dualComboBox.addItem("")
        self.dualComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.dualComboBox, 3, 1, 1, 1)
        self.verboseLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.verboseLineEdit.setObjectName("verboseLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.verboseLineEdit, 12, 1, 1, 1)
        self.verboseLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.verboseLabel.setObjectName("verboseLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.verboseLabel, 12, 0, 1, 1)
        self.warmStartLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.warmStartLabel.setObjectName("warmStartLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.warmStartLabel, 13, 0, 1, 1)
        self.warmStartComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.warmStartComboBox.setObjectName("warmStartComboBox")
        self.warmStartComboBox.addItem("")
        self.warmStartComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.warmStartComboBox, 13, 1, 1, 1)
        self.l1RatioLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.l1RatioLabel.setObjectName("l1RatioLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.l1RatioLabel, 2, 0, 1, 1)
        self.l1RatioComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.l1RatioComboBox.setObjectName("l1RatioComboBox")
        self.l1RatioComboBox.addItem("")
        self.l1RatioComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.l1RatioComboBox, 2, 1, 1, 1)
        self.n_jobsLabel = QtWidgets.QLabel(self.advancedSettingsGroupBox)
        self.n_jobsLabel.setObjectName("n_jobsLabel")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.n_jobsLabel, 14, 0, 1, 1)
        self.n_jobsLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.n_jobsLineEdit.setObjectName("n_jobsLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.n_jobsLineEdit, 14, 2, 1, 1)
        self.l1RatioLineEdit = QtWidgets.QLineEdit(self.advancedSettingsGroupBox)
        self.l1RatioLineEdit.setObjectName("l1RatioLineEdit")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.l1RatioLineEdit, 2, 2, 1, 1)
        self.nJobsComboBox = QtWidgets.QComboBox(self.advancedSettingsGroupBox)
        self.nJobsComboBox.setObjectName("nJobsComboBox")
        self.nJobsComboBox.addItem("")
        self.nJobsComboBox.addItem("")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.nJobsComboBox, 14, 1, 1, 1)
        self.resetToDefaultPushButton = QtWidgets.QPushButton(self.advancedSettingsGroupBox)
        self.resetToDefaultPushButton.setObjectName("resetToDefaultPushButton")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.resetToDefaultPushButton, 15, 0, 1, 1)
        self.cancelPushButton = QtWidgets.QPushButton(self.advancedSettingsGroupBox)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.cancelPushButton, 15, 1, 1, 1)
        self.applyPushButton = QtWidgets.QPushButton(self.advancedSettingsGroupBox)
        self.applyPushButton.setObjectName("applyPushButton")
        self.advancedSettingsGroupBoxGridLayout.addWidget(self.applyPushButton, 15, 2, 1, 1)
        self.advancedSettingsGroupBoxGridLayout.setColumnStretch(0, 1)
        self.advancedSettingsGroupBoxGridLayout.setColumnStretch(1, 2)
        self.advancedSettingsGroupBoxGridLayout.setColumnStretch(2, 2)
        self.gridLayout.addLayout(self.advancedSettingsGroupBoxGridLayout, 0, 0, 1, 1)
        self.mainGridLayout.addWidget(self.advancedSettingsGroupBox, 0, 0, 2, 3)
        self.horizontalLayout.addLayout(self.mainGridLayout)

        self.retranslateUi(AdvancedSettingsLogReg)
        QtCore.QMetaObject.connectSlotsByName(AdvancedSettingsLogReg)
        AdvancedSettingsLogReg.setTabOrder(self.solverComboBox, self.penaltyComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.penaltyComboBox, self.l1RatioComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.l1RatioComboBox, self.l1RatioLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.l1RatioLineEdit, self.dualComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.dualComboBox, self.toleranceLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.toleranceLineEdit, self.inverseRegLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.inverseRegLineEdit, self.interceptComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.interceptComboBox, self.interceptScaleLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.interceptScaleLineEdit, self.classWeightComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.classWeightComboBox, self.randomStateComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.randomStateComboBox, self.randomStateLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.randomStateLineEdit, self.max_iterLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.max_iterLineEdit, self.multi_classComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.multi_classComboBox, self.verboseLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.verboseLineEdit, self.warmStartComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.warmStartComboBox, self.nJobsComboBox)
        AdvancedSettingsLogReg.setTabOrder(self.nJobsComboBox, self.n_jobsLineEdit)
        AdvancedSettingsLogReg.setTabOrder(self.n_jobsLineEdit, self.resetToDefaultPushButton)
        AdvancedSettingsLogReg.setTabOrder(self.resetToDefaultPushButton, self.cancelPushButton)
        AdvancedSettingsLogReg.setTabOrder(self.cancelPushButton, self.applyPushButton)

    def retranslateUi(self, AdvancedSettingsLogReg):
        _translate = QtCore.QCoreApplication.translate
        AdvancedSettingsLogReg.setWindowTitle(_translate("AdvancedSettingsLogReg", "Form"))
        self.advancedSettingsGroupBox.setTitle(_translate("AdvancedSettingsLogReg", "Advanced Settings Logistic Regression"))
        self.interceptScaleLineEdit.setText(_translate("AdvancedSettingsLogReg", "1.0"))
        self.inverseRegLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Inverse of regularization strength; must be a positive float. Like in support vector machines, smaller values specify stronger regularization.</p></body></html>"))
        self.inverseRegLabel.setText(_translate("AdvancedSettingsLogReg", "Inverse regularization strenght:"))
        self.inverseRegLineEdit.setText(_translate("AdvancedSettingsLogReg", "1.0"))
        self.label.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Specifies if a constant (a.k.a. bias or intercept) should be added to the decision function.</p></body></html>"))
        self.label.setText(_translate("AdvancedSettingsLogReg", "Intercept:"))
        self.max_iterLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Maximum number of iterations taken for the solvers to converge.</p></body></html>"))
        self.max_iterLabel.setText(_translate("AdvancedSettingsLogReg", "Maximum iterations:"))
        self.multi_classLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>If the option chosen is ‘ovr’, then a binary problem is fit for each label. For ‘multinomial’ the loss minimised is the multinomial loss fit across the entire probability distribution, <span style=\" font-style:italic;\">even when the data is binary</span>. ‘multinomial’ is unavailable when solver=’liblinear’. ‘auto’ selects ‘ovr’ if the data is binary, or if solver=’liblinear’, and otherwise selects ‘multinomial’.</p></body></html>"))
        self.multi_classLabel.setText(_translate("AdvancedSettingsLogReg", "Multi class:"))
        self.randomStateLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Used when <span style=\" font-family:\'Courier New\';\">solver</span> == ‘sag’, ‘saga’ or ‘liblinear’ to shuffle the data.</p></body></html>"))
        self.randomStateLabel.setText(_translate("AdvancedSettingsLogReg", "Random state:"))
        self.solverComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "newton-cg"))
        self.solverComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "lbfgs"))
        self.solverComboBox.setItemText(2, _translate("AdvancedSettingsLogReg", "liblinear"))
        self.solverComboBox.setItemText(3, _translate("AdvancedSettingsLogReg", "sag"))
        self.solverComboBox.setItemText(4, _translate("AdvancedSettingsLogReg", "saga"))
        self.penaltyLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Used to specify the norm used in the penalization. The ‘newton-cg’, ‘sag’ and ‘lbfgs’ solvers support only l2 penalties. ‘elasticnet’ is only supported by the ‘saga’ solver. If ‘none’ (not supported by the liblinear solver), no regularization is applied.</p></body></html>"))
        self.penaltyLabel.setText(_translate("AdvancedSettingsLogReg", "Penalty:"))
        self.interceptComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "False"))
        self.interceptComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "True"))
        self.max_iterLineEdit.setText(_translate("AdvancedSettingsLogReg", "100"))
        self.randomStateComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "Integer"))
        self.randomStateComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "None"))
        self.penaltyComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "l1"))
        self.penaltyComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "l2"))
        self.penaltyComboBox.setItemText(2, _translate("AdvancedSettingsLogReg", "elasticnet"))
        self.penaltyComboBox.setItemText(3, _translate("AdvancedSettingsLogReg", "None"))
        self.solverLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Algorithm to use in the optimization problem.</p><ul style=\"margin-top: 0px; margin-bottom: 0px; margin-left: 0px; margin-right: 0px; -qt-list-indent: 1;\"><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">For small datasets, ‘liblinear’ is a good choice, whereas ‘sag’ and ‘saga’ are faster for large ones.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">For multiclass problems, only ‘newton-cg’, ‘sag’, ‘saga’ and ‘lbfgs’ handle multinomial loss; ‘liblinear’ is limited to one-versus-rest schemes.</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">‘newton-cg’, ‘lbfgs’, ‘sag’ and ‘saga’ handle L2 or no penalty</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">‘liblinear’ and ‘saga’ also handle L1 penalty</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">‘saga’ also supports ‘elasticnet’ penalty</li><li style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">‘liblinear’ does not support setting <span style=\" font-family:\'Courier New\';\">penalty=\'none\'</span></li></ul><p>Note that ‘sag’ and ‘saga’ fast convergence is only guaranteed on features with approximately the same scale.</p></body></html>"))
        self.solverLabel.setText(_translate("AdvancedSettingsLogReg", "Solver:"))
        self.classWeightLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Weights associated with classes in the form <span style=\" font-family:\'Courier New\';\">{class_label: weight}</span>. If not given, all classes are supposed to have weight one.</p><p>The “balanced” mode uses the values of y to automatically adjust weights inversely proportional to class frequencies in the input data as <span style=\" font-family:\'Courier New\';\">n_samples / (n_classes * np.bincount(y))</span>.</p><p>Note that these weights will be multiplied with sample_weight (passed through the fit method) if sample_weight is specified.</p></body></html>"))
        self.classWeightLabel.setText(_translate("AdvancedSettingsLogReg", "Class weight:"))
        self.interceptScaleLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Useful only when the solver ‘liblinear’ is used and self.fit_intercept is set to True. In this case, x becomes [x, self.intercept_scaling], i.e. a “synthetic” feature with constant value equal to intercept_scaling is appended to the instance vector. The intercept becomes <span style=\" font-family:\'Courier New\';\">intercept_scaling * synthetic_feature_weight</span>.</p><p>Note! the synthetic feature weight is subject to l1/l2 regularization as all other features. To lessen the effect of regularization on synthetic feature weight (and therefore on the intercept) intercept_scaling has to be increased.</p></body></html>"))
        self.interceptScaleLabel.setText(_translate("AdvancedSettingsLogReg", "Intercept Scale:"))
        self.multi_classComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "ovr"))
        self.multi_classComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "multinomial"))
        self.multi_classComboBox.setItemText(2, _translate("AdvancedSettingsLogReg", "auto"))
        self.classWeightComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "None"))
        self.classWeightComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "BALANCED"))
        self.toleranceLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Tolerance for stopping criteria.</p></body></html>"))
        self.toleranceLabel.setText(_translate("AdvancedSettingsLogReg", "Tolerance value:"))
        self.dualLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>Dual or primal formulation. Dual formulation is only implemented for l2 penalty with liblinear solver. Prefer dual=False when n_samples &gt; n_features.</p></body></html>"))
        self.dualLabel.setText(_translate("AdvancedSettingsLogReg", "Dual or primal formulation:"))
        self.toleranceLineEdit.setText(_translate("AdvancedSettingsLogReg", "0.0001"))
        self.dualComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "dual"))
        self.dualComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "primal"))
        self.verboseLineEdit.setText(_translate("AdvancedSettingsLogReg", "0"))
        self.verboseLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>For the liblinear and lbfgs solvers set verbose to any positive number for verbosity.</p></body></html>"))
        self.verboseLabel.setText(_translate("AdvancedSettingsLogReg", "Verbose:"))
        self.warmStartLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>When set to True, reuse the solution of the previous call to fit as initialization, otherwise, just erase the previous solution. Useless for liblinear solver</p></body></html>"))
        self.warmStartLabel.setText(_translate("AdvancedSettingsLogReg", "Warm start:"))
        self.warmStartComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "False"))
        self.warmStartComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "True"))
        self.l1RatioLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p>The Elastic-Net mixing parameter, with <span style=\" font-family:\'Courier New\';\">0 &lt;= l1_ratio &lt;= 1</span>. Only used if <span style=\" font-family:\'Courier New\';\">penalty=\'elasticnet\'</span>. Setting <span style=\" font-family:\'Courier New\';\">l1_ratio=0</span> is equivalent to using <span style=\" font-family:\'Courier New\';\">penalty=\'l2\'</span>, while setting <span style=\" font-family:\'Courier New\';\">l1_ratio=1</span> is equivalent to using <span style=\" font-family:\'Courier New\';\">penalty=\'l1\'</span>. For <span style=\" font-family:\'Courier New\';\">0 &lt; l1_ratio &lt;1</span>, the penalty is a combination of L1 and L2.</p></body></html>"))
        self.l1RatioLabel.setText(_translate("AdvancedSettingsLogReg", "l1 ratio:"))
        self.l1RatioComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "None"))
        self.l1RatioComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "Float"))
        self.n_jobsLabel.setToolTip(_translate("AdvancedSettingsLogReg", "<html><head/><body><p><span style=\" color:#000000;\">Number of CPU cores used when parallelizing over classes if multi_class=’ovr’”. This parameter is ignored when the </span><span style=\" font-family:\'Courier New\'; color:#000000;\">solver</span><span style=\" color:#000000;\"> is set to ‘liblinear’ regardless of whether ‘multi_class’ is specified or not. </span><span style=\" font-family:\'Courier New\'; color:#000000;\">None</span><span style=\" color:#000000;\"> means 1 unless in</span><span style=\" color:#000000;\"> a </span><a href=\"https://joblib.readthedocs.io/en/latest/parallel.html#joblib.parallel_backend\"><span style=\" font-family:\'Courier New\'; color:#000000;\">joblib.parallel_backend</span></a><span style=\" color:#000000;\"> co</span><span style=\" color:#000000;\">ntext. </span><span style=\" font-family:\'Courier New\'; color:#000000;\">-1</span><span style=\" color:#000000;\"> means using all processors.</span></p></body></html>"))
        self.n_jobsLabel.setText(_translate("AdvancedSettingsLogReg", "Number of jobs:"))
        self.nJobsComboBox.setItemText(0, _translate("AdvancedSettingsLogReg", "None"))
        self.nJobsComboBox.setItemText(1, _translate("AdvancedSettingsLogReg", "Integer"))
        self.resetToDefaultPushButton.setText(_translate("AdvancedSettingsLogReg", "Reset"))
        self.cancelPushButton.setText(_translate("AdvancedSettingsLogReg", "Cancel"))
        self.applyPushButton.setText(_translate("AdvancedSettingsLogReg", "Apply"))
